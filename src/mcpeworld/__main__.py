
import argparse
import os
import sys

from mcpeworld import Str
from mcpeworld.application import Application
from mcpeworld.database import createEngine, createSession
from mcpeworld.database.repository import (
    EffectRepository,
    EnchantmentRepository,
    ItemRepository,
    TrimMaterialRepository,
    TrimPatternRepository,
    UpdateMetaRepository,
)
from mcpeworld.network.scraper import WikiScraper


def runUpdate( updateType:Str ) -> None:
    engine = createEngine()
    session = createSession( engine )
    scraper = WikiScraper(
        ItemRepository( session ),
        EnchantmentRepository( session ),
        EffectRepository( session ),
        UpdateMetaRepository( session ),
        TrimMaterialRepository( session ),
        TrimPatternRepository( session ),
    )
    if updateType == "item":
        scraper.updateItems()
    elif updateType == "enchantment":
        scraper.updateEnchantments()
    elif updateType == "effect":
        scraper.updateEffects()
    elif updateType == "trim":
        scraper.updateTrims()
    elif updateType == "all":
        scraper.updateAll()


def main() -> None:
    os.system( "clear" )
    parser = argparse.ArgumentParser(
        prog="mcpeworld",
        description="MCPE Bedrock World Editor CLI"
    )
    parser.add_argument(
        "--update-item",
        action="store_true",
        help="Update item database from Minecraft Wiki"
    )
    parser.add_argument(
        "--update-enchantment",
        action="store_true",
        help="Update enchantment database"
    )
    parser.add_argument(
        "--update-effect",
        action="store_true",
        help="Update effect database from Minecraft Wiki"
    )
    parser.add_argument(
        "--update-trim",
        action="store_true",
        help="Update trim material/pattern database from Minecraft Wiki"
    )
    parser.add_argument(
        "--update-all",
        action="store_true",
        help="Update all databases"
    )
    args = parser.parse_args()
    if args.update_all:
        runUpdate( "all" )
        return
    if args.update_item:
        runUpdate( "item" )
        return
    if args.update_enchantment:
        runUpdate( "enchantment" )
        return
    if args.update_effect:
        runUpdate( "effect" )
        return
    if args.update_trim:
        runUpdate( "trim" )
        return
    app = Application()
    try:
        app.run()
    except KeyboardInterrupt:
        print( "\nExiting." )
        sys.exit( 0 )


if __name__ == "__main__":
    main()
