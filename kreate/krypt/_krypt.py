import logging
import os
import base64
import sys
import jinja2.filters
from pathlib import Path

from ..kore import Cli, Konfig, Module
from . import krypt_functions

logger = logging.getLogger(__name__)

def dekrypt_bytes(self, b: bytes) -> bytes:
    return krypt_functions.dekrypt_bytes(b)

def dekrypt_str(self, s: str) -> str:
    return krypt_functions.dekrypt_str(s)

class KryptModule(Module):
    def init_konfig(self, konfig: Konfig):
        self.konfig = konfig # TODO: this is not really how this is intended
        krypt_functions._key_finder = self
        konfig.dekrypt_bytes = dekrypt_bytes
        konfig.dekrypt_str   = dekrypt_str

    def init_cli(self, cli: Cli):
        jinja2.filters.FILTERS["dekrypt"] = krypt_functions.dekrypt_str
        cli.add_help_section("krypt commands:")
        self.add_krypt_options(cli)
        self.add_krypt_subcommands(cli)

    def process_cli_options(self, cli: Cli):
        if cli.args.testdummy:
            krypt_functions._dekrypt_testdummy = True

    def get_krypt_key(self):
        krypt_key = self.default_krypt_key().encode()
        return base64.b64encode(krypt_key).decode()

    def default_krypt_key(self):
        env_varname = self.default_krypt_key_env_var()
        logger.debug(f"getting dekrypt key from {env_varname}")
        psw = os.getenv(env_varname)
        if not psw:
            logger.warning(f"no dekrypt key given in environment var {env_varname}")
        return psw

    def default_krypt_key_env_var(self):
        varname = self.konfig.get_path("system", {}).get("krypt_key_varname", None)
        env = self.konfig.get_path("app.env")
        return varname or "KREATE_KRYPT_KEY_" + env.upper()

    def add_krypt_options(self, cli: Cli):
        cli.parser.add_argument(
            "--testdummy", action="store_true", help="do not dekrypt values"
        )

    def add_krypt_subcommands(self, cli: Cli):
        cli.add_subcommand(dekrypt, aliases=["dek"])
        cli.add_subcommand(enkrypt, aliases=["enk"])

def aliases():
    return {
        "f": "file",
        "s": "string",
        "str": "string",
        "l": "lines",
        "k": "lines",
    }


def dekrypt(cli: Cli):
    """dekrypt lines|string|file <file> (abbrevs l|s|str|f)"""
    subcmd = cli.params[0]
    subcmd = aliases().get(subcmd, subcmd)
    if subcmd == "file":
        dekfile(cli)
    elif subcmd == "string":
        dekstr(cli)
    elif subcmd == "lines":
        dek_lines(cli)
    else:
        raise ValueError(f"unknow dekrypt subcommand {subcmd}")


def enkrypt(cli: Cli):
    """enkrypt lines|string|file <file> (abbrevs l|s|str|f)"""
    subcmd = cli.params[0]
    subcmd = aliases().get(subcmd, subcmd)
    if subcmd == "file":
        enkfile(cli)
    elif subcmd == "string":
        enkstr(cli)
    elif subcmd == "lines":
        enk_lines(cli)
    else:
        raise ValueError(f"unknow dekrypt subcommand {subcmd}")


def dek_lines(cli: Cli):
    """dekrypt lines in a text file"""
    konfig = cli.kreate_konfig()
    files = cli.params[1]
    files = files or Path(konfig.dir).glob("secret*konf")
    for f in files:
        logger.warning(f"dekrypting: {f}")
        krypt_functions.dekrypt_lines(f, ".")


def dekstr(cli: Cli):
    """dekrypt string value"""
    cli.kreate_konfig()  # init konfig to set the secret value
    value = None if len(cli.params)==1 else cli.params[1]
    if not value:
        if not cli.args.quiet:
            print("Enter string to dekrypt")
        value = sys.stdin.readline().strip()
        print(krypt_functions.dekrypt_str(value))
    else:
        print(krypt_functions.dekrypt_str(str))


def dekfile(cli: Cli):
    "dekrypt an entire file"
    cli.kreate_konfig()  # init konfig to set the secret value
    for f in cli.params[1]:
        logger.info(f"dekrypting file {f}")
        krypt_functions.dekrypt_file(f)


def enk_lines(cli: Cli):
    "enkrypt lines in a text file"
    konfig: Konfig = cli.kreate_konfig()
    files = cli.params[1]
    files = files or Path(konfig.dir).glob("secret*konf")
    for f in files:
        logger.warning(f"enkrypting: {f}")
        krypt_functions.enkrypt_lines(f, ".")


def enkfile(cli: Cli):
    "enkrypt an entire file"
    cli.kreate_konfig()
    for f in cli.params[1]:
        logger.info(f"enkrypting file {f}")
        krypt_functions.enkrypt_file(f)


def enkstr(cli: Cli):
    """enkrypt string value"""
    cli.kreate_konfig()
    value = None if len(cli.params)==1 else cli.params[1]
    if not value:
        if not cli.args.quiet:
            print("Enter string to enkrypt")
        value = sys.stdin.readline().strip()
    print(krypt_functions.enkrypt_str(value))
