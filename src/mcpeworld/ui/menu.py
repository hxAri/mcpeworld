from typing import Callable, MutableSequence, Optional, Tuple

from prompt_toolkit import prompt as ptPrompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import clear

from mcpeworld import Bool, Int, Str


def showMenu( title:Str, options:MutableSequence[Tuple[Str, Str]] ) -> Int:
    print( f"\n{'=' * 50}" )
    print( f"  {title}" )
    print( f"{'=' * 50}" )
    for i, ( label, description ) in enumerate( options ):
        desc = f" - {description}" if description else ""
        print( f"  [{i + 1}] {label}{desc}" )
    print( f"  [0] Back / Cancel" )
    print()
    while True:
        try:
            raw = ptPrompt( "Select option: " )
            choice = int( raw.strip() )
            if 0 <= choice <= len( options ):
                return choice
            print( f"  Invalid choice. Enter 0-{len( options )}." )
        except ( ValueError, EOFError, KeyboardInterrupt ):
            return 0


def showListMenu( title:Str, items:MutableSequence[Str], extraOptions:MutableSequence[Tuple[Int, Str]] = None ) -> Int:
    print( f"\n{'=' * 50}" )
    print( f"  {title}" )
    print( f"{'=' * 50}" )
    for i, item in enumerate( items ):
        print( f"  [{i + 1}] {item}" )
    if extraOptions:
        print()
        for key, label in extraOptions:
            print( f"  [{key}] {label}" )
    print( f"  [0] Back" )
    print()
    while True:
        try:
            raw = ptPrompt( "Select: " )
            choice = int( raw.strip() )
            validExtras = {k for k, _ in ( extraOptions or [] )}
            if choice == 0 or 1 <= choice <= len( items ) or choice in validExtras:
                return choice
            print( f"  Invalid choice." )
        except ( ValueError, EOFError, KeyboardInterrupt ):
            return 0


def promptInput( label:Str, default:Str = "" ) -> Str:
    suffix = f" [{default}]" if default else ""
    try:
        raw = ptPrompt( f"{label}{suffix}: " )
        result = raw.strip()
        return result if result else default
    except ( EOFError, KeyboardInterrupt ):
        return default


def promptInt( label:Str, default:Int = 0 ) -> Int:
    while True:
        raw = promptInput( label, str( default ) )
        try:
            return int( raw )
        except ValueError:
            print( "  Enter a valid integer." )


def promptFloat( label:Str, default:float = 0.0 ) -> float:
    while True:
        raw = promptInput( label, str( default ) )
        try:
            return float( raw )
        except ValueError:
            print( "  Enter a valid number." )


def promptBool( label:Str, default:Bool = False ) -> Bool:
    suffix = "Y/n" if default else "y/N"
    raw = promptInput( f"{label} ({suffix})", "" )
    if not raw:
        return default
    return raw.lower() in ( "y", "yes", "true", "1" )


def promptChoice( label:Str, choices:MutableSequence[Tuple[Int, Str]], default:Int = 0 ) -> Int:
    print( f"\n  {label}:" )
    for value, name in choices:
        marker = " *" if value == default else ""
        print( f"    [{value}] {name}{marker}" )
    return promptInt( "  Choice", default )


def promptSearchItem( label:Str, itemNames:MutableSequence[Str] ) -> Str:
    completer = WordCompleter( itemNames, ignore_case=True )
    try:
        result = ptPrompt( f"{label}: ", completer=completer )
        return result.strip()
    except ( EOFError, KeyboardInterrupt ):
        return ""


def confirmAction( message:Str ) -> Bool:
    return promptBool( message, default=False )
