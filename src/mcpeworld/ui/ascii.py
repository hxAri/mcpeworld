from pathlib import Path
from typing import MutableMapping, MutableSequence, Tuple

from PIL import Image

from mcpeworld import Bool, Int, Str
from mcpeworld.constant import ResourcesDir
from mcpeworld.model.item import BEGameItem

AsciiChars:Str = " .:-=+*#%@"

FrontAsciiPath:Path = ResourcesDir / "armor.ascii"
BackAsciiPath:Path = ResourcesDir / "armor_back.ascii"
SideAsciiPath:Path = ResourcesDir / "armor_side.ascii"

DimCharMap:MutableMapping[Str, Str] = {
    "5": ".", "Y": ".", "J": ".",
    "?": "^", "7": "~", "!": "~",
    "~": " ", "^": " ", ".": " ",
}

FrontRegions:MutableMapping[Str, Tuple[Int, Int]] = {
    "head": ( 1, 10 ),
    "chest": ( 11, 20 ),
    "legs": ( 21, 36 ),
    "boots": ( 37, 43 ),
}

BackRegions:MutableMapping[Str, Tuple[Int, Int]] = {
    "head": ( 1, 10 ),
    "chest": ( 11, 20 ),
    "legs": ( 21, 36 ),
    "boots": ( 37, 43 ),
}

SideRegions:MutableMapping[Str, Tuple[Int, Int]] = {
    "head": ( 1, 10 ),
    "chest": ( 11, 20 ),
    "legs": ( 21, 36 ),
    "boots": ( 37, 43 ),
}

SlotRegionKeys:MutableSequence[Str] = ["head", "chest", "legs", "boots"]


def renderWorldIcon( imagePath:Path, width:Int = 60 ) -> Str:
    if not imagePath.is_file():
        return "(no world icon)"
    image = Image.open( imagePath )
    aspectRatio = image.height / image.width
    height = int( width * aspectRatio * 0.45 )
    image = image.resize( ( width, height ) )
    image = image.convert( "L" )
    lines:MutableSequence[Str] = []
    for y in range( height ):
        row:MutableSequence[Str] = []
        for x in range( width ):
            pixel = image.getpixel( ( x, y ) )
            charIndex = pixel * ( len( AsciiChars ) - 1 ) // 255
            row.append( AsciiChars[charIndex] )
        lines.append( "".join( row ) )
    return "\n".join( lines )


def _loadTemplate( path:Path ) -> MutableSequence[Str]:
    if not path.is_file():
        return []
    with open( path, "r" ) as f:
        content = f.read()
    lines = content.split( "\n" )
    if lines and not lines[0].strip():
        lines = lines[1:]
    if lines and not lines[-1].strip():
        lines = lines[:-1]
    return lines


def _dimLine( line:Str ) -> Str:
    result:MutableSequence[Str] = []
    for ch in line:
        result.append( DimCharMap.get( ch, ch ) )
    return "".join( result )


def _accentBorders( line:Str ) -> Str:
    stripped = line.rstrip()
    if not stripped:
        return line
    firstNonSpace = -1
    lastNonSpace = -1
    for i, ch in enumerate( stripped ):
        if ch != " ":
            if firstNonSpace < 0:
                firstNonSpace = i
            lastNonSpace = i
    if firstNonSpace < 0:
        return line
    chars = list( line )
    if firstNonSpace < len( chars ) and chars[firstNonSpace] != " ":
        chars[firstNonSpace] = "*"
    if firstNonSpace + 1 < len( chars ) and chars[firstNonSpace + 1] != " ":
        chars[firstNonSpace + 1] = "*"
    if lastNonSpace < len( chars ) and chars[lastNonSpace] != " ":
        chars[lastNonSpace] = "*"
    if lastNonSpace - 1 >= 0 and chars[lastNonSpace - 1] != " ":
        chars[lastNonSpace - 1] = "*"
    return "".join( chars )


def _hasTrim( item:BEGameItem ) -> Bool:
    return not item.isEmpty and bool( item.trimPattern ) and bool( item.trimMaterial )


def _renderTemplate(
    templateLines:MutableSequence[Str],
    regions:MutableMapping[Str, Tuple[Int, Int]],
    armorItems:MutableSequence[BEGameItem]
) -> MutableSequence[Str]:
    head = armorItems[0] if len( armorItems ) > 0 else BEGameItem()
    chest = armorItems[1] if len( armorItems ) > 1 else BEGameItem()
    legs = armorItems[2] if len( armorItems ) > 2 else BEGameItem()
    boots = armorItems[3] if len( armorItems ) > 3 else BEGameItem()
    slotItems = {
        "head": head,
        "chest": chest,
        "legs": legs,
        "boots": boots,
    }
    result:MutableSequence[Str] = []
    for lineIndex, line in enumerate( templateLines ):
        slotKey = ""
        for key, ( start, end ) in regions.items():
            if start <= lineIndex <= end:
                slotKey = key
                break
        if slotKey and slotKey in slotItems:
            item = slotItems[slotKey]
            if item.isEmpty:
                line = _dimLine( line )
            elif _hasTrim( item ):
                line = _accentBorders( line )
        result.append( line )
    return result


def _itemLabel( item:BEGameItem, slotName:Str ) -> Str:
    if item.isEmpty:
        return f"{slotName}: (Empty)"
    name = item.itemName
    if _hasTrim( item ):
        return f"{slotName}: {name} [{item.trimPattern}/{item.trimMaterial}]"
    return f"{slotName}: {name}"


def _combineViewsHorizontal(
    viewsList:MutableSequence[MutableSequence[Str]],
    gap:Int = 3
) -> MutableSequence[Str]:
    maxLines = max( len( v ) for v in viewsList )
    widths:MutableSequence[Int] = []
    for view in viewsList:
        w = max( ( len( line ) for line in view ), default=0 )
        widths.append( w )
        while len( view ) < maxLines:
            view.append( "" )
    combined:MutableSequence[Str] = []
    separator = " " * gap
    for lineIndex in range( maxLines ):
        parts:MutableSequence[Str] = []
        for viewIndex, view in enumerate( viewsList ):
            line = view[lineIndex]
            parts.append( line.ljust( widths[viewIndex] ) )
        combined.append( separator.join( parts ).rstrip() )
    return combined


def renderArmorFront( armorItems:MutableSequence[BEGameItem] ) -> Str:
    templateLines = _loadTemplate( FrontAsciiPath )
    if not templateLines:
        return "(armor template not found)"
    rendered = _renderTemplate( templateLines, FrontRegions, armorItems )
    head = armorItems[0] if len( armorItems ) > 0 else BEGameItem()
    chest = armorItems[1] if len( armorItems ) > 1 else BEGameItem()
    legs = armorItems[2] if len( armorItems ) > 2 else BEGameItem()
    boots = armorItems[3] if len( armorItems ) > 3 else BEGameItem()
    offhand = armorItems[4] if len( armorItems ) > 4 else BEGameItem()
    labelMap:MutableMapping[Int, Str] = {
        2: _itemLabel( head, "Head" ),
        5: _itemLabel( chest, "Chest" ),
        8: _itemLabel( legs, "Legs" ),
        10: _itemLabel( boots, "Boots" ),
    }
    if not offhand.isEmpty:
        labelMap[12] = _itemLabel( offhand, "Off Hand" )
    result:MutableSequence[Str] = []
    for i, line in enumerate( rendered ):
        label = labelMap.get( i, "" )
        if label:
            result.append( f"  {line}  {label}" )
        else:
            result.append( f"  {line}" )
    return "\n".join( result )


def renderArmorFull( armorItems:MutableSequence[BEGameItem] ) -> Str:
    frontLines = _loadTemplate( FrontAsciiPath )
    backLines = _loadTemplate( BackAsciiPath )
    sideLines = _loadTemplate( SideAsciiPath )
    if not frontLines:
        return "(armor templates not found)"
    renderedFront = _renderTemplate( frontLines, FrontRegions, armorItems )
    renderedBack = _renderTemplate( backLines, BackRegions, armorItems ) if backLines else []
    renderedSide = _renderTemplate( sideLines, SideRegions, armorItems ) if sideLines else []
    views:MutableSequence[MutableSequence[Str]] = [renderedFront]
    viewNames:MutableSequence[Str] = ["Front"]
    if renderedBack:
        views.append( renderedBack )
        viewNames.append( "Back" )
    if renderedSide:
        views.append( renderedSide )
        viewNames.append( "Side" )
    combined = _combineViewsHorizontal( views, gap=3 )
    head = armorItems[0] if len( armorItems ) > 0 else BEGameItem()
    chest = armorItems[1] if len( armorItems ) > 1 else BEGameItem()
    legs = armorItems[2] if len( armorItems ) > 2 else BEGameItem()
    boots = armorItems[3] if len( armorItems ) > 3 else BEGameItem()
    offhand = armorItems[4] if len( armorItems ) > 4 else BEGameItem()
    labels:MutableSequence[Str] = [
        _itemLabel( head, "Head" ),
        _itemLabel( chest, "Chest" ),
        _itemLabel( legs, "Legs" ),
        _itemLabel( boots, "Boots" ),
    ]
    if not offhand.isEmpty:
        labels.append( _itemLabel( offhand, "Off Hand" ) )
    result:MutableSequence[Str] = []
    for line in combined:
        result.append( f"  {line}" )
    result.append( "" )
    for label in labels:
        result.append( f"  {label}" )
    return "\n".join( result )
