--------------------------------------------------------------------------------
-- Constants
--------------------------------------------------------------------------------

local MAP = {
	OVERWORLD  = 0,
	UNDERWORLD = 1,
	MOON       = 2,
	DUNGEON    = 3,
}

local MAP_MAX = {
	[MAP.OVERWORLD]  = 256,
	[MAP.UNDERWORLD] = 128,
	[MAP.MOON]       = 64,
	[MAP.DUNGEON]    = 32,
}

local TRIGGER = {
	NORMAL = 1,
	DISTANT = 2,
	INVENTORY = 3,
}

local MAP_ID = 0x7E1701
local GAME_TIME = 0x7E16A3
local RNG_INDEX = 0x7E0097
local RNG_TABLE = 0x7E1900
local ENEMY_HP = 0x7E2287 -- + 0x80 * n
local ENEMY_POSITION = 0x7E29A5 -- 8x8
local BACK_ATTACK = 0x7E6CC0
local BATTLE = 0x7E0203 -- 0x7E0207
local PARTY_POSITION = 0x7EEFC5 -- + 0x10 * n
local ATB = 0x7E2A07 -- + 0x15 * n
local AGI = 0x7E2295
local RS = 0x7E2060
local CHAR_ACTIVE = 0x7E1000
local CHAR_LEVEL = 0x7E1002
local CHAR_EXP = 0x7E1037
local X = 0x7E1706
local Y = 0x7E1707
local LOCATION_TYPE = 0x7E1700 -- 0地上 1地底 2月 3街・ダンジョン

local ENCOUNT_RNG_INDEX = 0x7E0686 -- loop 0 -> 0xFF -> 0
local ENCOUNT_RNG_TABLE = 0x94EE00
local ENCOUNT_SHIFT = 0x7E17EF
local ENCOUNT_BORDER_EARTH = 0x8EC300
local ENCOUNT_BORDER_UNDER = 0x8EC340
local ENCOUNT_BORDER_MOON = 0x8EC341
local ENCOUNT_BORDER_DUNGEON = 0x8EC342
--local CRITICAL = 0x7E102D -- + 0x40 * n
local CRITICAL = 0x7E202D -- + 0x80 * n

--------------------------------------------------------------------------------
-- Variables
--------------------------------------------------------------------------------

local MEMORY = {}

--------------------------------------------------------------------------------
-- Memory Functions
--------------------------------------------------------------------------------

local function get_npc_offset(npc)
	local offset = 0

	for i = 1, npc do
		offset = (offset + 15) % 256
	end

	return offset
end

local function memory_read_u16_be(address)
	return memory.readbyte(address) * 256 + memory.readbyte(address + 1)
end

local function memory_read_u16_le(address)
	return memory.readbyte(address + 1) * 256 + memory.readbyte(address)
end

local function memory_read(key, index)
	if not index then
		index = 0
	end

	if key == "npc_pointer" or key == "npc_x_offset" or key == "npc_x" or key == "npc_y" or key == "npc_y_offset" or key == "npc_visible" then
		return MEMORY[key].f(MEMORY[key].address + get_npc_offset(index))
	else
		return MEMORY[key].f(MEMORY[key].address + index * MEMORY[key].record_size)
	end
end

--------------------------------------------------------------------------------
-- Memory Addresses
--------------------------------------------------------------------------------

MEMORY = {
	battle_party_level = {f = memory.readbyte,     address = 0x7E38D4, record_size = 1},
	battle_enemy_level = {f = memory.readbyte,     address = 0x7E38D5, record_size = 1},
	battle_formation   = {f = memory_read_u16_le,  address = 0x7E1800, record_size = 1},
	map_type        = {f = memory.readbyte,    address = 0x7E1700, record_size = 1},
	map_id          = {f = memory_read_u16_be, address = 0x7E1701, record_size = 1},
	map_x           = {f = memory.readbyte,    address = 0x7E1706, record_size = 1},
	map_y           = {f = memory.readbyte,    address = 0x7E1707, record_size = 1},
	map_vehicle     = {f = memory.readbyte,    address = 0x7E1704, record_size = 1},
	map_frames      = {f = memory.readbyte,    address = 0x7E067B, record_size = 1},
	menu_status     = {f = memory.readbyte,    address = 0x7E0500, record_size = 1},
	shop_status     = {f = memory.readbyte,    address = 0x7E06B1, record_size = 1},
	npc_count       = {f = memory.readbyte,    address = 0x7E08FE, record_size = 1},
	npc_x_offset    = {f = memory.readbyte,    address = 0x7E0903, record_size = 15},
	npc_x           = {f = memory.readbyte,    address = 0x7E0904, record_size = 15},
	npc_y_offset    = {f = memory.readbyte,    address = 0x7E0905, record_size = 15},
	npc_y           = {f = memory.readbyte,    address = 0x7E0906, record_size = 15},
	npc_pointer     = {f = memory.readbyte,    address = 0x7E0907, record_size = 15},
	npc_visible     = {f = memory.readbyte,    address = 0x7E090B, record_size = 15},
	npc_pointer_2   = {f = memory_read_u16_le, address = 0x139802, record_size = 2},
	text_data       = {f = memory.readbyte,    address = 0x7F4C00, record_size = 1},
	tile_data       = {f = memory_read_u16_be, address = 0x7E0EDB, record_size = 2},
	tile_index      = {f = memory.readbyte,    address = 0x7F5C71, record_size = 1},
	tile_offset_x   = {f = memory_read_u16_le, address = 0x7E066A, record_size = 1},
	tile_offset_y   = {f = memory_read_u16_le, address = 0x7E066C, record_size = 1},
	trigger_pointer = {f = memory_read_u16_le, address = 0x158000, record_size = 2},
}

--------------------------------------------------------------------------------
-- Map Functions
--------------------------------------------------------------------------------

local function wrap_coordinate(coordinate)
	local map_type = memory_read("map_type")

	if map_type == MAP.OVERWORLD or map_type == MAP.MOON then
		local adjustment = MAP_MAX[map_type]

		if coordinate < 0 then
			coordinate = coordinate + MAP_MAX[map_type]
		elseif coordinate >= MAP_MAX[map_type] then
			coordinate = coordinate - MAP_MAX[map_type]
		end
	end

	return coordinate
end

local function tile_has_trigger(map_id, x, y)
	local address = 0x158300
	local offset = memory_read("trigger_pointer", map_id)

	for i = 0, 0x10000 - 1 do
		local trigger_x = memory.readbyte(address + offset)
		local trigger_y = memory.readbyte(address + offset + 1)

		if x == trigger_x and y == trigger_y then
			if address + offset >= 0x160000 then
				return TRIGGER.DISTANT
			else
				return TRIGGER.NORMAL
			end
		end

		offset = offset + 5

		if address + offset >= 0x161440 and address + offset < 0x161470 then
			return TRIGGER.INVENTORY
		end
	end

	return TRIGGER.DISTANT
end

local function get_tile_data(x, y)
	local value = memory_read("tile_data", memory_read("tile_index", bit.band(y, 0x3F) * 256 + x))

	local tile = {
		mystery_bit_15 = bit.band(value, 0x8000) > 0,
		mystery_bit_14 = bit.band(value, 0x4000) > 0,
		mystery_bit_13 = bit.band(value, 0x2000) > 0,
		door           = bit.band(value, 0x1000) > 0,
	    save_point     = bit.band(value, 0x0800) > 0,
	    layer_bridge   = bit.band(value, 0x0400) > 0,
	    layer_2        = bit.band(value, 0x0200) > 0,
	    layer_1        = bit.band(value, 0x0100) > 0,
	    trigger        = bit.band(value, 0x0080) > 0,
	    encounters     = bit.band(value, 0x0040) > 0,
	    talk_over      = bit.band(value, 0x0020) > 0,
	    warp           = bit.band(value, 0x0010) > 0,
	    bottom_half    = bit.band(value, 0x0008) > 0,
	    walk_behind    = bit.band(value, 0x0004) > 0,
		mystery_bit_1  = bit.band(value, 0x0002) > 0,
	    damage_floor   = bit.band(value, 0x0001) > 0,
	}

	return tile
end

function is_boundary(x1, y1, x2, y2)
	local tile1 = get_tile_data(x1, y1)
	local tile2 = get_tile_data(x2, y2)

	if not tile1.layer_1 and not tile2.layer_1 and not tile1.layer_2 and not tile2.layer_2 then
		return false
	elseif tile1.layer_1 and tile2.layer_1 then
		return false
	elseif tile1.layer_2 and tile2.layer_2 then
		return false
	end

	return true
end

local function is_border_tile(map_type, x, y)
	local maximum = MAP_MAX[map_type]

	local border_x = (x == -1 or x == maximum)
	local border_y = (y == -1 or y == maximum)

	if border_x and y >= -1 and y <= maximum then
		return true
	elseif border_y and x >= -1 and x <= maximum then
		return true
	else
		return false
	end
end

local function get_tile_color(map_id, x, y)
	local map_type = memory_read("map_type")
	x = wrap_coordinate(x)
	y = wrap_coordinate(y)

	if not MAP_MAX[map_type] then
		return nil
	end

	if is_border_tile(map_type, x, y) then
		return "#00FF0080"
	elseif x < -1 or y < -1 or x > MAP_MAX[map_type] or y > MAP_MAX[map_type] then
		return "#FF000080"
	else
		local tile = get_tile_data(x, y)

		if tile.trigger then
			local trigger = tile_has_trigger(map_id, x, y)

			if trigger == TRIGGER.NORMAL then
				return "#00FFFFA0"
			elseif trigger == TRIGGER.INVENTORY then
				return "#FFFF0080"
			elseif trigger == TRIGGER.DISTANT then
				return "#FF800080"
			else
				return "#00FFFF40"
			end
		elseif tile.door then
			return "#FFFFFF80"
		elseif tile.warp then
			return "#00FF0080"
		elseif tile.talk_over then
			return "#FF00FF80"
		elseif tile.damage_floor then
			return "#0080FF80"
		elseif not tile.layer_1 and not tile.layer_2 and not tile.bridge_layer then
			return "#FF000080"
		elseif not tile.encounters then
			return "#0000FF80"
		end
	end
end

local function get_tile_offset(key, coordinate)
	local tile_offset = memory_read(key) - 120

	if coordinate > 135 or (coordinate == 134 and tile_offset == 0) or (coordinate == 135 and tile_offset ~= 2047) then
		tile_offset = tile_offset + 2048
	end

	if coordinate < 64 and tile_offset > 1024 then
		tile_offset = tile_offset - 2048
	end

	return tile_offset
end

local function draw_npc(pixel_x, pixel_y, npc)
	local npc_pointer = memory_read("npc_pointer", npc)

	if memory_read("map_id") >= 256 then
		npc_pointer = npc_pointer + 256
	end

	local npc_pointer = memory_read("npc_pointer_2", npc_pointer)
	local color = "#FFFFFFFF"

	if memory_read("npc_visible", npc) == 0 then
		color = "#808080FF"
	end

	gui.box(pixel_x, pixel_y, pixel_x + 15, pixel_y + 15, "#00000000", color)
	gui.text(pixel_x + 3, pixel_y + 2, npc)

	local value = memory.readbyte(0x139C00 + npc_pointer)

	--[[if npc == 3 then
		for i = 1, 15 do
			local address = 0x7E08FF + i - 1
			print(string.format('%X %d', address, memory.readbyte(address + get_npc_offset(npc))))
		end
	end]]

	if value == 0xFF then
		gui.box(pixel_x + 12, pixel_y + 2, pixel_x + 14, pixel_y + 4, color)
	end

	local box = false

	--[[for i = 1, 0x10000 do
		local pointer = 0x139C00 + npc_pointer

		if not box and pointer > 0x140000 then
			gui.box(pixel_x + 12, pixel_y + 2, pixel_x + 14, pixel_y + 4, "#FFFFFFFF")
			box = true
		end

		local value = memory.readbyte(0x139C00 + npc_pointer)

		if value == 0xFF then
			break
		end

		npc_pointer = npc_pointer + 1
	end]]
end

local function draw_tile(x, y, tile_color)
	local map_type = memory_read("map_type")
	local map_id = memory_read("map_id")
	local map_x = memory_read("map_x")
	local map_y = memory_read("map_y")

	local tile_offset_x = get_tile_offset("tile_offset_x", map_x)
	local tile_offset_y = get_tile_offset("tile_offset_y", map_y)

	local pixel_x = x * 16 - tile_offset_x - 1
	local pixel_y = y * 16 - tile_offset_y - 2

	local tile_color = get_tile_color(map_id, x, y)

	if tile_color then
		gui.box(pixel_x, pixel_y, pixel_x + 17, pixel_y + 17, tile_color, "#00000000")
	end

	if is_boundary(x, y, x - 1, y) then
		gui.line(pixel_x, pixel_y, pixel_x, pixel_y + 16, "#FF0000FF")
	end

	if is_boundary(x, y, x, y - 1) then
		gui.line(pixel_x, pixel_y, pixel_x + 16, pixel_y, "#FF0000FF")
	end

	local value = memory_read("text_data", y * 32 + x)

	if x > 0 and x < 32 and y > 0 and y < 32 and value > 0 and value ~= 255 then
		local npc = bit.band(value, 0x7F)
		local npc_x = memory_read("npc_x", npc)
		local npc_y = memory_read("npc_y", npc)

		if math.abs(npc_x - x) > 1 or math.abs(npc_y - y) > 1 then
			draw_npc(pixel_x + 1, pixel_y + 1, npc)
		end
	end

	if x == map_x and y == map_y then
		gui.box(pixel_x, pixel_y, pixel_x + 16, pixel_y + 16, "", "#00FF00FF")
	end
end

local function draw_tile_overlay()
	local x = memory.readbyte(X)
	local y = memory.readbyte(Y)

	for i = 0, 16 do
		for j = 0, 14 do
			local map_x = (x - 7) + i
			local map_y = (y - 7) + j

			draw_tile(map_x, map_y)
		end
	end
end

local function draw_npc_overlay()
	local npc_count = memory_read("npc_count")

	local map_x = memory.readbyte(X)
	local map_y = memory.readbyte(Y)

	for i = 0, npc_count - 1 do
		local npc_x = memory_read("npc_x", i)
		local npc_y = memory_read("npc_y", i)

		local npc_x_offset = memory_read("npc_x_offset", i)
		local npc_y_offset = memory_read("npc_y_offset", i)

		local tile_offset_x = get_tile_offset("tile_offset_x", map_x)
		local tile_offset_y = get_tile_offset("tile_offset_y", map_y)

		local pixel_x = npc_x * 16 - tile_offset_x + npc_x_offset
		local pixel_y = npc_y * 16 - tile_offset_y - 1 + npc_y_offset

		draw_npc(pixel_x, pixel_y, i)
	end
end

--------------------------------------------------------------------------------
-- Functions
--------------------------------------------------------------------------------

function is_warp(map, x, y)
	local tile_index = memory.readbyte(0x7F5C71 + (bit.band(y, 0x3F) * 256 + x))
	local value = memory.readbyte(0x7E0EDC + tile_index * 2)
	return bit.band(value, 0x10) > 0
end

function is_triggerable(map, x, y)
	local my_x = memory.readbyte(X)
	local my_y = memory.readbyte(Y)
	local my_tile_index = memory.readbyte(0x7F5C71 + (bit.band(my_y, 0x3F) * 256 + my_x))
	local my_value = memory.readbyte(0x7E0EDC + my_tile_index * 2)

	local tile_index = memory.readbyte(0x7F5C71 + (bit.band(y, 0x3F) * 256 + x))
	local value = memory.readbyte(0x7E0EDC + tile_index * 2)
	return bit.band(value, 0x80) > 0 and bit.band(value, 0x08) == 0 and bit.band(my_value, 0x08) == 0
end

function has_encounters(map, x, y)
	local tile_index = memory.readbyte(0x7F5C71 + (bit.band(y, 0x3F) * 256 + x))
	local value = memory.readbyte(0x7E0EDC + tile_index * 2)

	if (bit.band(value, 0x40) > 0) then
		return true
	else
		return false
	end
end

function can_walk(map, x, y)
	local tile_index = memory.readbyte(0x7F5C71 + (y * 256 + x))
	local value = memory.readbyte(0x7E0EDB + tile_index * 2)

	if (bit.band(value, 0x01) > 0) or bit.band(value, 0x02) > 0 then
		return true
	else
		return false
	end
end

function can_cross(x1, y1, x2, y2)
	local tile_index_1 = memory.readbyte(0x7F5C71 + (y1 * 256 + x1))
	local tile_index_2 = memory.readbyte(0x7F5C71 + (y2 * 256 + x2))

	local v1 = memory.readbyte(0x7E0EDB + tile_index_1 * 2)
	local v2 = memory.readbyte(0x7E0EDB + tile_index_2 * 2)

	local test1 = bit.band(v1, 0x01) > 0 and bit.band(v2, 0x01) > 0
	local test2 = bit.band(v1, 0x02) > 0 and bit.band(v2, 0x02) > 0
	local test3 = bit.band(v1, 0x04) > 0 and bit.band(v2, 0x04) > 0

	return test1 or test2 or test3
end

function dialog()
	if memory.readbyte(0x7E02F8) == 0x2C or memory.readbyte(0x7E02EF) == 0x2C or memory.readbyte(0x7E02F4) == 0x2C then
		joypad.set({["A"] = true})
	end
end

function exp()
	--printEXP(0, 1)
	--printEXP(1, 3)
	--printEXP(2, 0)
	--printEXP(3, 4)
	--printEXP(4, 2)

	--printEXP(6, 5)
	--printEXP(7, 6)
	--printEXP(8, 7)
	--printEXP(9, 8)
	--printEXP(10,9)
end

local battle_start = nil
local last_battle_frames = 0

function main()
	if battle_start ~= nil then
		last_battle_frames = emu.framecount() - battle_start
	end

	if memory.readbyte(BATTLE) == 0 then
		battle_start = nil
		--if memory_read("menu_status") ~= 1 and memory_read("shop_status") ~= 1 then
		if memory_read("menu_status") == 0 then
			dialog()
			draw_tile_overlay()
			draw_npc_overlay()
			encount()
			exp()
		end
	else
		if battle_start == nil then
			battle_start = emu.framecount()
		end

		battle()
		exp()
	end

	displayTime()

	--gui.box(0, 0, 96, 96, "#00000040", "#00000040")

end

function printText(row, col, text)
	gui.text(4 * col + 4, 8 * row, text)
end

function printEXP(row, i)
	local msg

	local offset = 0

	if row > 5 then
		offset = 60
		row = row - 6
	end

	if (i >= 5) then
		slot = string.format("S%d", i - 4)
	else
		slot = string.format("%d", i + 1)
	end

	if (memory.readbyte(CHAR_ACTIVE + i * 0x40) == 0) then
		msg = string.format("%2s:", slot)
	else
		msg = string.format("%2s: %2d %d", slot, getLevel(i), getEXP(i))
	end

	gui.text(4 + offset, 4 + 8 * row, msg)
end

function getEXP(i)
	local EXP = {}

	EXP[1] = memory.readbyte(CHAR_EXP + i * 0x40 + 0)
	EXP[2] = memory.readbyte(CHAR_EXP + i * 0x40 + 1)
	EXP[3] = memory.readbyte(CHAR_EXP + i * 0x40 + 2)

	return EXP[1] + EXP[2] * 256 + EXP[3] * 65536
end

function getLevel(i)
	return memory.readbyte(CHAR_LEVEL + i * 0x40)
end

function getMapAreaIndex(group, x, y)
	local description = getMapArea(group, x, y)

	indexes = {
		["Overworld (Baron)"] = 0,
		["Overworld (Mist)"] = 1,
		["Overworld (Kaipo)"] = 2,
		["Overworld (Damcyan)"] = 3,
		["Overworld (Fabul)"] = 4,
		["Overworld (Mysidia)"] = 5,
		["Overworld (Mt.Ordeals)"] = 6,
		["Overworld (Toroia)"] = 7,
		["Overworld (Chocobo Island)"] = 8,
		["Overworld (West Baron Peninsula)"] = 9,
		["Overworld (Eblan)"] = 10,
		["Overworld (Silvera/Toroia)"] = 7,
		["Underworld (Castle of Dwarves)"] = 0,
		["Underworld (Tomra)"] = 1,
		["Underworld (Three Step Peninsula)"] = 2,
		["Lunar Overworld"] = 0,
	}

	if indexes[description] ~= nil then
		return indexes[description]
	else
		return 65536
	end
end

function getMapArea(group, x, y)
	if group == 0 and x >= 0 and x < 256 and y >= 0 and y < 256 then
		if x >= 64 and x < 128 and y >= 128 and y < 192 then
			return "Overworld (Baron)"
		elseif x >= 64 and x < 96 and y >= 96 and y < 128 then
			return "Overworld (Mist)"
		elseif (x >= 96 and x < 160 and y >= 64 and y < 128) or (x >= 128 and x < 192 and y >= 96 and y < 160) then
			return "Overworld (Kaipo)"
		elseif  x >= 96 and x < 160 and y >= 0 and y < 64 then
			return "Overworld (Damcyan)"
		elseif (x >= 160 and x < 256 and y >= 0 and y < 96) or (x >= 192 and x < 256 and y >= 96 and y < 128) or (x >= 224 and x < 256 and y >= 128 and y < 160) then
			return "Overworld (Fabul)"
		elseif x >= 128 and x < 160 and y >= 160 and y < 256 then
			return "Overworld (Mysidia)"
		elseif x >= 160 and x < 256 and y >= 160 and y < 256 then
			return "Overworld (Mt.Ordeals)"
		elseif (x >= 0 and x < 64 and y >= 0 and y < 128) or (x >= 64 and x < 96 and y >= 0 and y < 64) then
			return "Overworld (Toroia)"
		elseif x >= 64 and x < 96 and y >= 64 and y < 96 then
			return "Overworld (Chocobo Island)"
		elseif x >= 0 and x < 64 and y >= 128 and y < 160 then
			return "Overworld (West Baron Peninsula)"
		elseif x >= 128 then
			return "Overworld (Silvera/Toroia)"
		else
			return "Overworld (Eblan)"
		end
	elseif group == 1 and x >= 0 and x < 128 and y >= 0 and y < 128 then
		if x >= 32 and x < 128 and y >= 0 and y < 96 then
			return "Underworld (Castle of Dwarves)"
		elseif x >= 0 and x < 32 and y >= 32 and y < 64 then
			return "Underworld (Three Step Peninsula)"
		else
			return "Underworld (Tomra)"
		end
	elseif group == 2 and x >= 0 and x < 64 and y >= 0 and y < 64 then
		return "Lunar Overworld"
	end

	return "N/A"
end

mapDescriptions = {
	[0]   = "Town of Baron",
	[1]   = "Village Mist",
	[2]   = "Kaipo",
	[3]   = "Mysidia",
	[4]   = "Silvera",
	[5]   = "Town of Toroia",
	[6]   = "Agart",
	[7]   = "Town of Toroia Inn",
	[8]   = "Town of Toroia Weapon Shop",
	[9]   = "Town of Toroia Armor Shop",
	[10]  = "Town of Toroia Item Shop",
	[11]  = "Town of Baron Inn",
	[12]  = "Town of Baron Weapon Shop",
	[13]  = "Town of Baron House (Cid)",
	[14]  = "Town of Baron House (Rosa)",
	[15]  = "Village Mist House",
	[16]  = "Kaipo Inn",
	[17]  = "Kaipo Cafe",
	[18]  = "Kaipo House",
	[19]  = "Mysidia Cafe",
	[20]  = "Mysidia Inn",
	[21]  = "Mt.Ordeals Tomb",
	[22]  = "Mysidia House of Wishes",
	[23]  = "Mysidia Room of Wishes",
	[24]  = "Town of Toroia Cafe 1F",
	[25]  = "Town of Toroia Cafe 2F",
	[26]  = "Town of Toroia Cafe Saloon KING",
	[28]  = "Town of Toroia Black Chocobo Farm",
	[29]  = "Town of Toroia Black Chocobo Farm Basement",
	[30]  = "Agart Astro Tower",
	[31]  = "Agart Astro Tower Observatory",
	[32]  = "Agart Inn",
	[33]  = "Chocobo's Village",
	[36]  = "Castle Baron",
	[37]  = "Damcyan",
	[38]  = "Fabul",
	[39]  = "Toroian Castle",
	[40]  = "Eblan",
	[42]  = "Castle Baron 1F",
	[43]  = "Castle Baron 2F",
	[44]  = "Castle Baron King's Room",
	[45]  = "Castle Baron Left Passage",
	[46]  = "Castle Baron Right Passage",
	[47]  = "Castle Baron Dungeon Antechamber",
	[48]  = "Castle Baron Dungeon",
	[49]  = "Castle Baron Infirmary",
	[50]  = "Castle Baron Left Tower 1F",
	[51]  = "Castle Baron Left Tower 2F",
	[52]  = "Castle Baron Left Tower Room",
	[53]  = "Castle Baron Right Tower 1F",
	[54]  = "Castle Baron Right Tower 2F",
	[55]  = "Castle Baron Right Tower 3F",
	[56]  = "Castle Baron Right Tower B1F",
	[57]  = "Castle Baron Right Tower B2F",
	[58]  = "Old Water-way",
	[59]  = "Castle Baron B3F",
	[60]  = "Castle Baron B1F",
	[61]  = "Castle Baron B1F Save Room",
	[62]  = "Castle Baron B2F",
	[63]  = "Damcyan 1F",
	[64]  = "Damcyan 2F",
	[65]  = "Damcyan 3F",
	[66]  = "Damcyan Basement",
	[67]  = "Damcyan B1F",
	[68]  = "Old Water-way Antechamber",
	[69]  = "Agart Weapon Shop",
	[70]  = "Agart Armor Shop",
	[71]  = "Fabul 1F",
	[72]  = "Fabul 2F",
	[73]  = "Fabul King's Room",
	[74]  = "Fabul Crystal Room",
	[75]  = "Fabul Weapons/Armors",
	[76]  = "Fabul Inn",
	[77]  = "Fabul Right Tower 1F",
	[78]  = "Fabul Right Tower 2F",
	[79]  = "Fabul Right Tower 3F",
	[80]  = "Fabul Left Tower 1F",
	[81]  = "Fabul Left Tower 2F",
	[82]  = "Fabul Left Tower 3F",
	[83]  = "Village Mist Clearing",
	[84]  = "Watery Pass-South B2F Save Room",
	[85]  = "Toroian Castle 1F",
	[86]  = "Toroian Castle 2F",
	[87]  = "Toroian Castle Crystal Room",
	[88]  = "Toroian Castle Infirmary",
	[89]  = "Toroian Castle B1F Antechamber",
	[90]  = "Toroian Castle B1F Left",
	[91]  = "Toroian Castle B1F Center",
	[92]  = "Toroian Castle B1F Right",
	[93]  = "Toroian Castle B2F",
	[94]  = "Eblan 1F",
	[95]  = "Eblan 2F",
	[96]  = "Eblan King's Room",
	[97]  = "Eblan Left Tower 1F",
	[98]  = "Eblan Left Tower 2F",
	[99]  = "Eblan Right Tower 1F",
	[100] = "Eblan Right Tower 2F",
	[101] = "Eblan Basement",
	[102] = "Castle Baron Black Magic Class",
	[103] = "Castle Baron White Magic Class",
	[104] = "Beach (outside Mysidia)",
	[106] = "Waterfalls Waterfall",
	[108] = "Misty Cave",
	[111] = "Watery Pass-South B1F",
	[112] = "Watery Pass-South B2F",
	[113] = "Watery Pass-South B3F",
	[114] = "Watery Pass-North B2F",
	[115] = "Watery Pass-North B1F",
	[116] = "Waterfalls B1F",
	[117] = "Waterfalls B2F",
	[118] = "Waterfalls Lake",
	[119] = "Antlion B1F",
	[120] = "Antlion B2F",
	[121] = "Antlion's Nest",
	[122] = "Antlion B1F Save Room",
	[123] = "Antlion B2F Treasure Room",
	[124] = "Black Background",
	[126] = "Mt.Hobs-West",
	[127] = "Mt.Hobs Summit",
	[128] = "Mt.Hobs-East",
	[129] = "Mt.Hobs-West Treasure Area",
	[131] = "Watery Pass-South B1F Treasure Room",
	[132] = "Mt.Ordeals",
	[133] = "Mt.Ordeals-3rd station",
	[134] = "Mt.Ordeals-7th station",
	[135] = "Mt.Ordeals Summit",
	[136] = "Mysidia Crystal Room",
	[137] = "Mysidia Serpent Road",
	[138] = "Castle Baron 3F",
	[139] = "Agart Well",
	[140] = "Cave Magnes B1F",
	[141] = "Cave Magnes B2F",
	[142] = "Cave Magnes B2F Treasure Room",
	[143] = "Cave Magnes B3F",
	[144] = "Cave Magnes B3F Treasure Room",
	[145] = "Cave Magnes B3F Passage",
	[146] = "Cave Magnes B3F Save Room",
	[147] = "Cave Magnes B4F",
	[148] = "Cave Magnes Crystal Room",
	[150] = "Watery Pass-South B2F Save Room Camp",
	[151] = "Town of Baron Serpent Road",
	[152] = "Tower of Zot 1F",
	[153] = "Tower of Zot 2F",
	[154] = "Tower of Zot 3F",
	[155] = "Falling Black Background",
	[156] = "Tower of Zot 4F",
	[157] = "Tower of Zot 5F",
	[158] = "Tower of Zot 6F",
	[159] = "Tower of Zot 7F",
	[160] = "Grotto Adamant",
	[161] = "Cave Magnes B4F Save Room",
	[162] = "Tower of Zot 5F Save Room",
	[163] = "Airship (Giant of Bab-il scene/Baron)",
	[164] = "Airship (Giant of Bab-il scene/Mysidia)",
	[165] = "Airship (Giant of Bab-il scene/Toroia)",
	[166] = "Tower of Bab-il B3F Save Room",
	[167] = "Tower of Bab-il 1F",
	[168] = "Tower of Bab-il B2F",
	[169] = "Tower of Bab-il B3F",
	[170] = "Tower of Bab-il B4F",
	[171] = "Tower of Bab-il Crystal Room",
	[172] = "Tower of Bab-il B5F",
	[173] = "Falling Cliff Background",
	[177] = "Training Room 1F",
	[178] = "Training Room 2F",
	[181] = "Giant of Bab-il Mouth",
	[182] = "Giant of Bab-il Neck",
	[183] = "Giant of Bab-il Chest",
	[185] = "Giant of Bab-il Stomach",
	[186] = "Giant of Bab-il Passage",
	[188] = "Giant of Bab-il Lung",
	[189] = "Giant of Bab-il CPU",
	[192] = "Airship (flying above Overworld)",
	[193] = "Port of Fabul",
	[194] = "Ship (at sea)",
	[195] = "Airship (docked)",
	[196] = "Two Airships (hovering above Overworld)",
	[198] = "Airship (flying above Underworld)",
	[199] = "Cave Eblana B1F",
	[200] = "Cave Eblana B2F",
	[201] = "Pass to Bab-il (south)",
	[202] = "Pass to Bab-il (north)",
	[203] = "Cave Eblana B2F Inn",
	[204] = "Cave Eblana B2F Weapons/Armors",
	[205] = "Pass to Bab-il (north) Save Room",
	[206] = "Cave Eblana B2F Infirmary",
	[207] = "Fabul Chocobo's Forest",
	[208] = "Airship (hovering above Overworld near Baron)",
	[209] = "Mt.Ordeals Chocobo's Forest",
	[210] = "Baron Chocobo's Forest",
	[211] = "Toroia Chocobo's Forest",
	[212] = "Chocobo Island Chocobo's Forest",
	[213] = "Castle Baron Hidden Passage",
	[214] = "Airship (remodeling)",
	[215] = "Airship (hovering above Overworld near Agart)",
	[217] = "Airship (landed)",
	[218] = "Mysidia Room of Wishes (final boss scene)",
	[224] = "Village Mist Inn",
	[225] = "Village Mist Weapon Shop",
	[226] = "Village Mist Armor Shop",
	[227] = "Kaipo Weapon Shop",
	[228] = "Kaipo Armor Shop",
	[229] = "Mysidia Weapon Shop",
	[230] = "Mysidia Armor Shop",
	[231] = "Mysidia Item Shop",
	[232] = "Silvera Inn",
	[233] = "Silvera Weapon Shop",
	[234] = "Silvera Armor Shop",
	[235] = "Silvera Item Shop",
	[236] = "Town of Baron Item Shop",
	[237] = "House of Wishes (ending)",
	[238] = "Pond (ending)",
	[239] = "Eblan King's Room (ending)",
	[240] = "Town of Monsters King's Room (ending)",
	[241] = "Damcyan 3F (ending)",
	[242] = "Castle of Dwarves (ending)",
	[243] = "Mt.Ordeals-7th station (ending)",
	[244] = "Agart Astro Tower Observatory (ending)",
	[245] = "Castle Baron Left Tower Room (ending)",
	[246] = "Castle Baron King's Room (ending)",
	[247] = "Fabul King's Room (ending)",
	[256] = "Kokkol, the Smith's",
	[257] = "Tomra",
	[258] = "Kokkol, the Smith's 1F",
	[259] = "Kokkol, the Smith's 2F",
	[260] = "Tomra Inn",
	[261] = "Tomra Weapons/Armors",
	[262] = "Tomra Treasure Room",
	[263] = "Castle of Dwarves",
	[264] = "Castle of Dwarves 1F",
	[265] = "Castle of Dwarves King's Room",
	[266] = "Castle of Dwarves B1F",
	[267] = "Castle of Dwarves B2F",
	[269] = "Castle of Dwarves Crystal Room",
	[270] = "Castle of Dwarves Right Tower 2F",
	[271] = "Castle of Dwarves Dwarf Base",
	[272] = "Castle of Dwarves Right Tower 3F",
	[273] = "Castle of Dwarves Left Tower 2F",
	[274] = "Castle of Dwarves Infirmary",
	[275] = "Castle of Dwarves Left Tower 3F",
	[276] = "Tower of Bab-il Save Room/Empty Room",
	[277] = "Tower of Bab-il 2F Treasure Room B (IceBrand)",
	[278] = "Tower of Bab-il 2F Treasure Room A (Blizzard)",
	[279] = "Tower of Bab-il 4F Treasure Room A (Ice Shield)",
	[280] = "Tower of Bab-il 4F Treasure Room B (Ice Armor)",
	[281] = "Castle of Dwarves Right Tower 5F",
	[282] = "Castle of Dwarves Left Tower 5F",
	[283] = "Castle of Dwarves 4F",
	[285] = "Tower of Bab-il 8F (revisit)",
	[286] = "Tower of Bab-il 7F (revisit)",
	[287] = "Tower of Bab-il 6F (revisit)",
	[288] = "Castle of Dwarves Cafe HOWDY!",
	[289] = "Tower of Bab-il 1F",
	[290] = "Tower of Bab-il 2F",
	[291] = "Tower of Bab-il 3F",
	[292] = "Tower of Bab-il 4F",
	[293] = "Tower of Bab-il 5F",
	[294] = "Tower of Bab-il 6F",
	[295] = "Tower of Bab-il 7F",
	[296] = "Tower of Bab-il 8F",
	[300] = "The Big Whale (Giant of Bab-il scene)",
	[301] = "Tower of Bab-il 5F Super Cannon",
	[302] = "Dwarf Tank",
	[303] = "The Big Whale",
	[306] = "Tomra Item Shop",
	[310] = "Land of Monsters B1F",
	[311] = "Land of Monsters B2F",
	[312] = "Land of Monsters B3F",
	[314] = "Land of Monsters B4F",
	[315] = "Land of Monsters Treasure Room",
	[316] = "Town of Monsters",
	[317] = "Town of Monsters Save Room",
	[318] = "Town of Monsters Library",
	[319] = "Town of Monsters Library Downstairs",
	[320] = "Town of Monsters King's Room",
	[321] = "Town of Monsters Weapon Shop",
	[322] = "Town of Monsters Armor Shop",
	[323] = "Town of Monsters Inn",
	[324] = "Sealed Cave",
	[325] = "Sylvan Cave B1F",
	[326] = "Sylvan Cave B2F",
	[327] = "Sylvan Cave B3F",
	[328] = "Sylvan Cave Treasure Room",
	[329] = "Sylvan House",
	[330] = "Sealed Cave B1F",
	[331] = "Sealed Cave B1F Treasure Room",
	[332] = "Sealed Cave B1F Passage",
	[333] = "Sealed Cave B2F",
	[334] = "Sealed Cave B2F Treasure Room C (Long/Ninja)",
	[335] = "Sealed Cave B2F Treasure Room B (various)",
	[336] = "Sealed Cave B2F Treasure Room A (Light)",
	[337] = "Sealed Cave B2F Passage",
	[338] = "Sealed Cave B3F",
	[339] = "Sealed Cave B3F Passage",
	[340] = "Sealed Cave B3F Treasure Room",
	[341] = "Sealed Cave B4F",
	[342] = "Sealed Cave B4F Save Room",
	[343] = "Sealed Cave B5F",
	[344] = "Sealed Cave Save Room/Empty Room",
	[345] = "Sealed Cave Crystal Room",
	[346] = "Cave Bahamut B1F",
	[347] = "Cave Bahamut B2F",
	[348] = "Cave Bahamut B3F",
	[352] = "Lunar's Lair 1F",
	[353] = "Lunar's Lair 2F",
	[355] = "Lunar Path (west)",
	[356] = "Lunar Path (east)",
	[357] = "Hummingway Cave",
	[359] = "Lunar Subterrane B1",
	[360] = "Lunar Subterrane B2",
	[361] = "Lunar Subterrane B3",
	[362] = "Lunar Subterrane B4",
	[363] = "Lunar Subterrane B5",
	[364] = "Lunar Subterrane B6",
	[365] = "Lunar Subterrane B7",
	[366] = "Lunar Core B1",
	[367] = "Lunar Core B2",
	[368] = "Lunar Core B3",
	[369] = "Lunar Core B4",
	[370] = "Lunar Core B5",
	[371] = "Lunar Subterrane B4 Treasure Room",
	[372] = "Lunar Subterrane B4 Passage",
	[373] = "Lunar Subterrane B5 Passage A",
	[374] = "Lunar Subterrane B5 Passage B",
	[375] = "Lunar Subterrane B5 Pink Puff Room",
	[376] = "Lunar Subterrane B5 Save Room",
	[377] = "Lunar Subterrane B6 Passage",
	[378] = "Lunar Subterrane B7 Treasure Room A (White)",
	[379] = "Lunar Subterrane B7 Save Room",
	[380] = "Lunar Subterrane B7 Treasure Room B (Ribbon)",
}

function getMapDescription(map)
	local description = mapDescriptions[map]

	if description then
		return description
	else
		return "N/A"
	end
end

local previous_step_index = nil
local previous_zone = nil
local previous_map = nil
local previous_x = nil
local previous_y = nil
local steps = 0
local walking_tiles = 0

local VEHICLE = {
	NONE = 0,
	CHOCOBO = 1,
	BLACK_CHOCOBO = 2,
	HOVERCRAFT = 3,
	ENTERPRISE = 4,
	FALCON = 5,
	BIG_WHALE = 6,
}

function is_mid_tile()
	local frames = 16
	local vehicle = memory_read("map_vehicle")

	if vehicle == VEHICLE.CHOCOBO or vehicle == VEHICLE.HOVERCRAFT then
		frames = 8
	elseif vehicle == VEHICLE.BLACK_CHOCOBO then
		frames = 4
	elseif vehicle >= VEHICLE.ENTERPRISE then
		frames = 2
	end

	return memory_read("map_frames") % frames ~= 0
end

function encount()
	local group = memory.readbyte(LOCATION_TYPE)
	local zone = memory.readbyte(MAP_ID - 1)
	local map = memory.readbyte(MAP_ID) * 256 + memory.readbyte(MAP_ID + 1)
	local x = memory.readbyte(X)
	local y = memory.readbyte(Y)
	local floor = memory.readwordsigned(0x7E172C) / 3

	local frame = memory.readbyte(0x7E0FFF)
	local index = memory.readbyte(ENCOUNT_RNG_INDEX)
	local seed = memory.readbyte(ENCOUNT_SHIFT)
	local rng = memory.readbyterange(ENCOUNT_RNG_TABLE, 256)
	local rate

	if previous_map == nil or map ~= previous_map or (zone ~= previous_zone and walking_tiles ~= 0) then
		steps = 0
		walking_tiles = 0
		previous_map = map
		previous_zone = zone
		previous_x = x
		previous_y = y
		previous_step_index = index
	else
		if previous_step_index == nil or index ~= previous_step_index then
			steps = steps + 1
			previous_step_index = index
		end

		if previous_x == nil or previous_x ~= x or previous_y ~= y then
			walking_tiles = walking_tiles + 1
			previous_x = x
			previous_y = y
		end
	end

	if group == 0 then
		local offset = bit.band(bit.rshift(y, 2), 0xF8) + bit.rshift(x, 5)
		rate = memory.readbyte(ENCOUNT_BORDER_EARTH + offset)
	elseif group == 1 then
		rate = memory.readbyte(ENCOUNT_BORDER_UNDER)
	elseif group == 2 then
		rate = memory.readbyte(ENCOUNT_BORDER_MOON)
	else
		rate = memory.readbyte(ENCOUNT_BORDER_DUNGEON + map)
	end

	--gui.box(0, 116, 96, 208, "#00000040", "#00000040")

	printText(13, 0, string.format("Floor: %2d", floor))

	if group == 3 then
		printText(14, 0, string.format("Map: %1d-%03d (%2d, %2d)", group, map, x, y))
		printText(15, 0, string.format("Description: %s", getMapDescription(map)))

		--local start = get_trigger_address(map, false)
		--local finish = get_trigger_address(map, true)

		--printText(16, 0, string.format("Triggers: %06X - %06X (%d)", start, finish, (finish - start) / 5))
	else
		printText(14, 0, string.format("Map: %1d-%03d (%2d, %2d)", group, getMapAreaIndex(group, x, y), x, y))
		printText(15, 0, string.format("Area: %s", getMapArea(group, x, y)))
	end

	printText(19, 0, string.format("Frame Counter:   %3d", frame))
	printText(20, 0, string.format("Step Seed:       %3d", seed))
	printText(21, 0, string.format("Step Index:      %3d %3d %3d", index, steps, walking_tiles))
	printText(22, 0, string.format("Encounter Rate:   %2d", rate))

	-- Encounter RNG Graph
	for i = 0, 255 do
		local value = rng[i + 1]
		local length = value
		local color = "#808080"

		-- Potential encounters (at maximum encounter rate)
		if (bit.band(value + seed, 0xFF) < 10) then
			color = "#550000"
			length = 255
		end

		-- Actual encounters (at current encounter rate)
		if (bit.band(value + seed, 0xFF) < rate) then
			color = "#FF0000"
			length = 255
		end

		-- Current value
		if (i == index) then
			color = "#FFFF00"
			length = 255
		end

		gui.drawline(i, 223 - length / 16, i, 223, color)
	end

	-- Encounter Groups
	local base = 0x8EC796
	local offset

	if group == 0 then
		local tmp = (bit.rshift(x, 5) + bit.band(bit.rshift(y, 2), 0xF8)) % 256
		offset = bit.lshift(memory.readbyte(0x8EC542 + tmp), 3)
	elseif group == 1 then
		local tmp = (bit.rshift(x, 5) + bit.band(bit.rshift(y, 3), 0xFC)) % 256
		offset = bit.lshift(memory.readbyte(0x8EC582 + tmp), 3)
	elseif group == 2 then
		local tmp = 0

		if y > 32 then
			tmp = 2
		end

		if x > 32 then
			tmp = tmp + 1
		end

		offset = bit.lshift(memory.readbyte(0x8EC592 + tmp), 3)
	else
		local tmp = memory.readbyte(0x7E1702)

		if memory.readbyte(0x7E1701) > 0 then
			tmp = tmp + 256
		end

		offset = bit.lshift(memory.readbyte(0x8EC596 + tmp), 3)
		base = 0x8EC816
	end

	printText(23, 0, string.format("Encounter Group: %3d", (base + offset - 0x8EC796) / 8))
	printText(24, 0, "Encounters:")

	for i = 0, 7 do
		local value = memory.readbyte(base + offset + i)

		if map >= 256 then
			value = value + 256
		end

		printText(24, 17 + i * 4, string.format("%3d", value))
	end

	if map >= 256 then
		printText(25, 0, "Encounters:")

		for i = 0, 7 do
			local value = memory.readbyte(base + offset + i)

			printText(25, 17 + i * 4, string.format("%3d", value))
		end
	end
end

function battle()
	for i = 0, 7 do
		local x = memory.readbyte(ENEMY_POSITION + i) / 2

		if (memory.readbyte(BACK_ATTACK) == 0) then
			x = x + 16
		else
			x = 256 - x - 32
		end

		if(memory.readword(ENEMY_HP + 0x80 * i) ~= 0) then
			gui.text(x,
				memory.readbyte(ENEMY_POSITION + i) % 0x10 * 8 + 0x10,
				string.format("HP: %d\nATB: %d\nAGI: %d/%d", memory.readword(ENEMY_HP + 0x80 * i), memory.readbyte(ATB + 0x15 * (i+5)), memory.readbyte(AGI + 0x80 * (i)), memory_read_u16_le(RS + 0x80 * (i + 5)))
			)
		end
	end


	for i = 0, 4 do
		local x = memory.readbyte(PARTY_POSITION + 0x10 * i)

		if (memory.readbyte(BACK_ATTACK) == 0) then
			x = x + 16
		else
			x = 256 - x - 16
		end

		gui.text(
			x,
			memory.readbyte(PARTY_POSITION + 0x10 * i + 1),
			string.format("%d\n%d/%d", memory.readbyte(ATB + 0x15 * i), memory.readbyte(AGI + 0x80 * (i - 5)), memory_read_u16_le(RS + 0x80 * i))
		)
	end


	local gameTime = memory.readbyterange(GAME_TIME, 4)
	local rngTable = memory.readbyterange(RNG_TABLE, 0x100)
	local index = memory.readbyte(RNG_INDEX)
	local color
	for i = 0, 0xFF do
		color = "#C0C0C0"

		if(getRNG(i, 0, 0xFF) < 128) then
			color = "#404040"
		elseif(getRNG(i, 0, 0xFF) < 208) then
			color = "#606060"
		elseif(getRNG(i, 0, 0xFF) < 252) then
			color = "#808080"
		end

		if(getRNG(i, 0, 0x62) < 5) then
			color = "#FF0000"
		end
		if(index == i) then
			color = "#FFFF00"
		end
		if( (index+gameTime[1])%256 == i) then
			color = "#00FF00"
		end

		gui.drawline(i, 0xDF - rngTable[i + 1] / 0x10, i, 0xDF, color)
	end

	gui.text(0x70, 0xB5, string.format("Levels: %d %d", memory_read("battle_party_level"), memory_read("battle_enemy_level")))
	gui.text(0x70, 0xBE, string.format("Formation: %d", memory_read("battle_formation")))
	gui.text(0x70, 0xC6, string.format("Index: %d", index))
	gui.text(0xA0, 0xC6, string.format("Frame: %d", gameTime[1] ))
--	gui.text(0xD0, 0xC6, string.format("Shift: %X", memory.readbyte(ENCOUNT_SHIFT)))
end




function displayTime()
	local gameTime = memory.readbyterange(GAME_TIME, 4)
	gui.text(0xA0, 1, string.format("Game Time %d:%02d:%05.2f",
		math.floor((gameTime[2] + gameTime[3] * 0x100 + gameTime[4] * 0x10000) / 3600),
		math.floor((gameTime[2] + gameTime[3] * 0x100 + gameTime[4] * 0x10000) % 3600 / 60),
		gameTime[2] % 60 + gameTime[1] / 60
	))
	gui.text(0xA0, 9, string.format("Real Time %d:%02d:%05.2f",
		math.floor((emu.framecount() + 1) / 216000),
		math.floor((emu.framecount() + 1) % 216000 / 3600),
		((emu.framecount() + 1) % 3600) / 60
	))
	gui.text(0xA0, 17, string.format("Frame     %10d", emu.framecount()))
	gui.text(0xA0, 25, string.format("Battle    %10d", last_battle_frames))
end



function getRNG(index, low, high)
	local rngTable = memory.readbyterange(RNG_TABLE, 0x100)

	if(low >= 255) then
		return low
	end
	if(high <= 0) then
		return high
	end
	if(low == high) then
		return high
	end

	if(high - low == 255) then
		return rngTable[index + 1]
	end

	return low + (rngTable[index + 1] % (high - low + 1))

end

function sumcheck(addr,n)
	local sum = 0
	for i=0,n-1 do
		sum = sum+memory.readword(addr+i)
	end
	return sum%0xFFFF
end

function midcheck(addr,n,mid)
	local st = 0x7E1000
	local sum = 0
	for i=0,mid-1 do
		sum = sum+memory.readword(st+i)
	end
	sum = sum+memory.readbyte(st+mid) + memory.readbyte(addr+mid+1)*256
	for i=mid+1,n-1 do
		sum = sum+memory.readword(addr+i)
	end

	return sum%0xFFFF
end

gui.register(main)
