import itertools
import sys
import threading

import click

SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
SPINNER_INTERVAL_SECONDS = 0.08


class Spinner:
    """Indicador simples de progresso em torno de uma chamada bloqueante ao agente.

    Um `agent.invoke(...)` pode levar alguns segundos sem nenhuma saída no meio, o que parece
    travado. Num terminal de verdade, anima em `stderr`; em qualquer outra saída (redirecionada,
    testes), imprime uma linha estática só, pra manter a saída determinística.
    """

    def __init__(self, message: str):
        self._message = message
        self._stop = threading.Event()
        self._thread = None

    def __enter__(self):
        if sys.stderr.isatty():
            self._thread = threading.Thread(target=self._spin, daemon=True)
            self._thread.start()
        else:
            click.echo(f"{self._message}...", err=True)
        return self

    def _spin(self):
        for frame in itertools.cycle(SPINNER_FRAMES):
            if self._stop.wait(SPINNER_INTERVAL_SECONDS):
                break
            sys.stderr.write(f"\r{frame} {self._message}...")
            sys.stderr.flush()

    def __exit__(self, *exc_info):
        if self._thread is not None:
            self._stop.set()
            self._thread.join()
            sys.stderr.write("\r\033[K")
            sys.stderr.flush()
