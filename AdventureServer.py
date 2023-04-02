"""
This is a Python module that exposes your Adventure.py as a webserver
"""
from typing import Dict
from aiohttp import web
from os import path
from datetime import datetime
import subprocess
import sys
import threading

ADVENTURE_PATH = path.join(path.dirname(path.realpath(__file__)), "Adventure.py")

class AdventureInstance(threading.Thread):
    """
    This class represents a single instance of your Adventure.py file.
    It's responsible for communicating between the web server and your
    Adventure.py file.
    """
    def __init__(self, name, **kwargs) -> None:
        super().__init__(**kwargs)

        self._name = name
        self._instance = None
        self._lock = threading.Lock()
        self._output = ""
        self._cv = threading.Condition(self._lock)
        self._done = False

    def run(self):
        try:
            # This is the code that runs your Adventure.py file.
            self._instance = subprocess.Popen(
                # python3 path/to/your/Adventure.py
                [sys.executable, ADVENTURE_PATH],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding="UTF-8",
            )

            while self._instance.poll() is None:
                text = self._instance.stdout.read(1)
                with self._cv:
                    self._output += text
                    self._cv.notify()
            with self._cv:
                self._output += self._instance.stdout.read()
                self._done = True
                self._cv.notify()
        finally:
            with self._cv:
                self._done = True
                self._cv.notify()
            print(f'[{datetime.now()}] [AdventureInstance: {self.name}]  âœ– Adventure.py exited')

    @property
    def name(self):
        return self._name

    @property
    def done(self):
        return self._done

    def is_prompting(self):
        return self._output.strip().endswith(">") or self._done

    def pop_content(self):
        with self._cv:
            self._cv.wait_for(self.is_prompting, 15)
            if self._done and not self._output:
                return None
            (out, sep, rest) = self._output.strip().rpartition("\n")
            self._output = ""
            if not sep:
                return rest
            return out

    def start_game(self):
        print(f'[{datetime.now()}] [AdventureInstance: {self.name}] -> Starting game')
        self.start()
        content = self.pop_content()
        print(f'[{datetime.now()}] [AdventureInstance: {self.name}] <- Returning Text: {content}')
        return content

    def end_game(self):
        print(f'[{datetime.now()}] [AdventureInstance: {self.name}] -> Ending game')
        self._instance.kill()
        self.join()
        print(f'[{datetime.now()}] [AdventureInstance: {self.name}] <- Successfully ended game')

    def run_command(self, command):
        print(f'[{datetime.now()}] [AdventureInstance: {self.name}] -> Got Command: {command}')
        self._instance.stdin.write(command + "\r\n")
        self._instance.stdin.flush()
        content = self.pop_content()
        print(f'[{datetime.now()}] [AdventureInstance: {self.name}] <- Returning Text: {content}')
        return content


class AdventureServer:
    def __init__(self) -> None:
        self._games: Dict[str, AdventureInstance] = {}

    async def reset_game(self, request: web.Request):
        name = request.match_info.get("name", None)
        if name is None:
            return web.Response(body="Must tell me which game to reset", status=400)
        if name in self._games:
            self._games[name].end_game()

        self._games[name] = AdventureInstance(name)
        return web.Response(body=self._games[name].start_game(), status=200)

    async def handle_command(self, request: web.Request):
        name = request.match_info.get("name", None)
        if name is None:
            return web.Response(body="Must tell me which game to command", status=400)
        if name not in self._games:
            return web.Response(body="That game does not exist", status=400)

        data = await request.text()
        response_text = self._games[name].run_command(data)
        if response_text is None or self._games[name].done:
            self._games[name].end_game()
            del self._games[name]
            return web.Response(body=response_text or "", status=200, headers={"X-Game-Finished": "true"})
        return web.Response(body=response_text, status=200)

    async def remove_game(self, request: web.Request):
        name = request.match_info.get("name", None)
        if name is None:
            return web.Response(body="Must tell me which game to command", status=400)
        if name not in self._games:
            return web.Response(body="That game does not exist", status=400)

        self._games[name].end_game()
        del self._games[name]


@web.middleware
async def cors(request: web.Request, handler):
    if request.method == "OPTIONS":
        response = web.Response(body="", status=204)
    else:
        response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response


def start_server():
    server = AdventureServer()
    app = web.Application(middlewares=[cors])
    app.add_routes(
        [
            web.put("/{name}/game", server.reset_game),
            web.post("/{name}/command", server.handle_command),
            web.delete("/{name}/game", server.remove_game),
        ]
    )
    web.run_app(app)


if __name__ == "__main__":
    start_server()