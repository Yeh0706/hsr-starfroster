"""Simplified Chinese / English strings."""

LANG = "zh"

PATHS = ["Destruction", "Hunt", "Erudition", "Harmony", "Nihility", "Preservation", "Abundance", "Remembrance", "Elation"]
BASE_TO_PATH = {"Warrior": "Destruction", "Rogue": "Hunt", "Mage": "Erudition", "Shaman": "Harmony",
                "Warlock": "Nihility", "Knight": "Preservation", "Priest": "Abundance", "Memory": "Remembrance",
                "Elation": "Elation"}
PATH_TO_BASE = {v: k for k, v in BASE_TO_PATH.items()}
ELEMENTS = ["Physical", "Fire", "Ice", "Thunder", "Wind", "Quantum", "Imaginary"]

_ZH = {
    "app_title": "Starfroster",
    # nav
    "nav_lineup": "编队", "nav_appearance": "角色外观", "nav_map": "切换地图", "nav_advanced": "高级",
    "nav_settings": "设置",
    # common
    "save": "保存", "discard": "放弃", "cancel": "取消", "ok": "确定", "add": "添加", "delete": "删除",
    "rename": "重命名", "remove": "移除", "move_up": "上移", "move_down": "下移", "close": "关闭",
    "unsaved": "有未保存的修改", "saved": "已保存", "saved_backup": "已保存（备份：{0}）",
    "save_failed": "保存失败", "error": "错误", "default": "默认", "unknown": "未知",
    "loading": "加载中…", "downloading": "下载中…", "download_failed": "下载失败", "done": "完成",
    # ppsr
    "ppsr_running": "ppsr 运行中", "ppsr_stopped": "ppsr 未运行", "ppsr_restart": "重启 ppsr",
    "ppsr_restart_title": "重启 ppsr？",
    "ppsr_restart_body": "将关闭正在运行的 ppsr.exe 并重新启动。游戏需要重新登录。",
    "ppsr_unsaved_title": "有未保存的修改",
    "ppsr_unsaved_body": "persistent.json 只在 ppsr 启动时读取一次。要先保存再重启吗？",
    "save_and_restart": "保存并重启", "restart_without_save": "不保存，直接重启",
    "ppsr_restarted": "ppsr 已重启，请重新登录游戏", "ppsr_not_found": "找不到 ppsr.exe：{0}",
    "ppsr_restart_failed": "重启 ppsr 失败",
    # file watching
    "file_changed_title": "文件已被外部修改",
    "file_changed_body": "persistent.json 在编辑器外被修改了。要重新读取吗？（会放弃你未保存的修改）",
    "reload": "重新读取", "keep_mine": "保留我的修改",
    "file_reloaded": "persistent.json 已被外部修改，已重新读取",
    "leader_moved": "原本的队长已移到第一位（队长固定为第一位）",
    "missing_persistent": "找不到 persistent.json，请在「设置」中选择 misc 文件夹",
    # lineup
    "lineup_title": "编队", "lineup_count": "{0} 人", "lineup_add": "添加角色",
    "lineup_empty": "还没有角色，点击「添加角色」",
    "lineup_hint": "拖曳卡片或用 ↑↓ 调整顺序。",
    "leader": "队长", "set_leader": "设为队长",
    "not_owned": "freesr-data 中没有这个角色，进游戏可能出问题",
    "rename_title": "自定义显示名称", "rename_hint": "留空则使用默认名称（只影响编辑器显示）",
    # picker
    "picker_title": "选择角色", "picker_search": "搜索 名称 / ID / 代号",
    "all_elements": "全部属性", "all_paths": "全部命途", "all_rarity": "全部星级",
    "owned_only": "只显示 freesr 中有的", "picker_selected": "已选 {0} 个", "picker_add": "加入编队",
    "in_lineup": "已在编队 #{0}",
    # appearance
    "appearance_title": "角色外观", "tab_tb": "命途", "tab_skin": "皮肤",
    "tb_group": "开拓者", "tb_gender": "开拓者性别", "tb_gender_desc": "星（女）或穹（男）",
    "female": "星（女）", "male": "穹（男）", "tb_path": "开拓者命途", "tb_path_desc": "开拓者当前的命途",
    "march_group": "三月七", "march_path": "三月七命途", "march_path_desc": "三月七当前的命途",
    "skin_add": "添加角色皮肤", "skin_other": "其他角色（输入 ID）…", "skin_empty": "没有皮肤设置",
    "skin_id_title": "输入角色 ID", "skin_value_custom": "皮肤 ID {0}",
    "skin_hint": "选择「默认」等于 0",
    # map
    "map_title": "切换地图", "map_current": "当前位置", "map_unknown_place": "不在地图列表中",
    "map_add_fav": "收藏", "tab_explore": "探索", "tab_combat": "战斗（拟造花萼）", "tab_beta": "测试服",
    "tab_fav": "我的收藏", "teleport": "传送", "map_search": "搜索地图",
    "tag_calyx": "可打花萼", "tag_beta": "测试服", "map_count": "{0} 个地图",
    "map_no_data": "还没有地图数据", "map_download": "下载地图数据",
    "teleported": "已设置为「{0}」，保存并重启 ppsr 后生效", "restart_now": "保存并重启",
    "fav_empty": "还没有收藏。可以在「当前位置」收藏目前的地点。",
    "fav_name_title": "收藏名称", "fav_default_name": "收藏 {0}",
    "fav_before_title": "当前位置还没有收藏",
    "fav_before_body": "当前位置（plane {0}）不在地图列表里，传送后就找不回来了。要先收藏吗？",
    "fav_and_teleport": "收藏后传送", "teleport_anyway": "直接传送",
    "fav_added": "已收藏", "plane": "plane {0}",
    # advanced
    "advanced_title": "高级", "tab_json": "原始 JSON", "tab_backup": "备份",
    "json_apply": "应用", "json_refresh": "从表单刷新", "json_ok": "格式正确",
    "json_error": "第 {0} 行第 {1} 列：{2}", "json_not_object": "最外层必须是 JSON 对象",
    "json_applied": "已应用到编辑器，记得保存", "json_hint": "修改后按「应用」，再保存。",
    "backup_empty": "还没有备份（每次保存前会自动备份）", "backup_restore": "还原",
    "backup_open": "打开备份文件夹", "backup_restored": "已载入备份 {0}，保存后生效",
    "backup_restore_title": "还原这个备份？",
    "backup_restore_body": "会把 {0} 的内容载入编辑器（尚未保存）。确认后再按保存才会写入。",
    "chg_lineup": "编队 {0}→{1} 人", "chg_scene": "地图 plane {0}→{1}", "chg_skin": "皮肤",
    "chg_tb_gender": "开拓者性别", "chg_tb_path": "开拓者命途", "chg_march_path": "三月七命途",
    "chg_other": "其他字段", "chg_none": "无改动",
    # settings
    "persistent_file": "persistent.json 位置", "choose_file": "选择文件",
    "shortcut": "建立快捷方式", "shortcut_desc": "在桌面或开始菜单建立 Starfroster 的快捷方式",
    "shortcut_desktop": "桌面", "shortcut_startmenu": "开始菜单",
    "shortcut_done": "已建立快捷方式", "shortcut_failed": "建立快捷方式失败",
    "pick_persistent_title": "选择 persistent.json",
    "pick_persistent_wrong": "请选择名为 persistent.json 的文件（在 ppSR 的 misc 文件夹里）",
    "first_run_title": "欢迎使用",
    "first_run_body": "第一次使用，请先选择要编辑的 persistent.json。\n它在 ppSR 文件夹的 misc 里，例如：\nC:\\StarRail Beta\\ppSR_REL_4.7.5X\\misc\\persistent.json",
    "settings_title": "设置", "grp_files": "文件", "misc_path": "misc 文件夹",
    "choose_folder": "选择文件夹", "misc_invalid": "这个文件夹里没有 persistent.json",
    "grp_look": "个性化", "theme": "应用主题", "theme_desc": "浅色、深色或跟随系统",
    "theme_auto": "跟随系统", "theme_light": "浅色", "theme_dark": "深色",
    "language": "语言", "language_desc": "重启编辑器后生效", "language_restart": "语言已更改，重启编辑器后生效",
    "grp_data": "数据", "map_data": "地图数据", "map_data_desc": "来源：Escape-penacony · 版本 {0} · 更新于 {1}",
    "map_data_none": "来源：Escape-penacony · 尚未下载",
    "char_data": "角色资源", "char_data_desc": "来源：nanoka.cc · 数据版本 {0} · {1} 个角色",
    "char_data_none": "来源：nanoka.cc · 尚未下载",
    "check_update": "检查更新", "updated": "已更新", "up_to_date": "已是最新",
    "clear_icons": "已清除图标缓存", "icon_cache": "图标缓存", "clear": "清除", "grp_about": "关于", "about": "关于",
    "about_desc": "Starfroster v{1} · ppSR persistent.json 编辑器 · 数据文件夹：{0}",
    "repo_desc": "源代码、问题回报与更新",
    "open_data_folder": "打开数据文件夹",
}

_EN = {
    "app_title": "Starfroster",
    "nav_lineup": "Lineup", "nav_appearance": "Appearance", "nav_map": "Teleport", "nav_advanced": "Advanced",
    "nav_settings": "Settings",
    "save": "Save", "discard": "Discard", "cancel": "Cancel", "ok": "OK", "add": "Add", "delete": "Delete",
    "rename": "Rename", "remove": "Remove", "move_up": "Move up", "move_down": "Move down", "close": "Close",
    "unsaved": "You have unsaved changes", "saved": "Saved", "saved_backup": "Saved (backup: {0})",
    "save_failed": "Save failed", "error": "Error", "default": "Default", "unknown": "Unknown",
    "loading": "Loading…", "downloading": "Downloading…", "download_failed": "Download failed", "done": "Done",
    "ppsr_running": "ppsr running", "ppsr_stopped": "ppsr stopped", "ppsr_restart": "Restart ppsr",
    "ppsr_restart_title": "Restart ppsr?",
    "ppsr_restart_body": "The running ppsr.exe will be closed and started again. You will need to log in to the game again.",
    "ppsr_unsaved_title": "Unsaved changes",
    "ppsr_unsaved_body": "persistent.json is only read when ppsr starts. Save before restarting?",
    "save_and_restart": "Save and restart", "restart_without_save": "Restart without saving",
    "ppsr_restarted": "ppsr restarted. Log in to the game again.", "ppsr_not_found": "ppsr.exe not found: {0}",
    "ppsr_restart_failed": "Failed to restart ppsr",
    "file_changed_title": "File changed outside the editor",
    "file_changed_body": "persistent.json was modified outside the editor. Reload it? (Your unsaved changes will be lost.)",
    "reload": "Reload", "keep_mine": "Keep my changes",
    "file_reloaded": "persistent.json changed outside the editor and was reloaded",
    "leader_moved": "The previous leader was moved to the first slot (the leader is always first)",
    "missing_persistent": "persistent.json not found. Choose the misc folder in Settings.",
    "lineup_title": "Lineup", "lineup_count": "{0} characters", "lineup_add": "Add characters",
    "lineup_empty": "No characters yet. Click \"Add characters\".",
    "lineup_hint": "Drag cards or use ↑↓ to reorder.",
    "leader": "Leader", "set_leader": "Set as leader",
    "not_owned": "This character is not in freesr-data and may cause problems in game",
    "rename_title": "Custom display name", "rename_hint": "Leave empty to use the default name (editor only)",
    "picker_title": "Choose characters", "picker_search": "Search name / ID / tag",
    "all_elements": "All elements", "all_paths": "All paths", "all_rarity": "All rarities",
    "owned_only": "Only characters in freesr", "picker_selected": "{0} selected", "picker_add": "Add to lineup",
    "in_lineup": "In lineup #{0}",
    "appearance_title": "Appearance", "tab_tb": "Paths", "tab_skin": "Skins",
    "tb_group": "Trailblazer", "tb_gender": "Trailblazer gender", "tb_gender_desc": "Stelle (female) or Caelus (male)",
    "female": "Stelle (female)", "male": "Caelus (male)", "tb_path": "Trailblazer path",
    "tb_path_desc": "The Trailblazer's current path",
    "march_group": "March 7th", "march_path": "March 7th path", "march_path_desc": "March 7th's current path",
    "skin_add": "Add skin", "skin_other": "Other character (enter ID)…", "skin_empty": "No skins set",
    "skin_id_title": "Character ID", "skin_value_custom": "Skin ID {0}", "skin_hint": "\"Default\" equals 0",
    "map_title": "Teleport", "map_current": "Current location", "map_unknown_place": "Not in the map list",
    "map_add_fav": "Favorite", "tab_explore": "Explore", "tab_combat": "Combat (Calyx)", "tab_beta": "Beta server",
    "tab_fav": "Favorites", "teleport": "Teleport", "map_search": "Search maps",
    "tag_calyx": "Calyx", "tag_beta": "Beta", "map_count": "{0} maps",
    "map_no_data": "No map data yet", "map_download": "Download map data",
    "teleported": "Set to \"{0}\". Save and restart ppsr to apply.", "restart_now": "Save and restart",
    "fav_empty": "No favorites yet. Save the current location from the card above.",
    "fav_name_title": "Favorite name", "fav_default_name": "Favorite {0}",
    "fav_before_title": "Current location is not saved",
    "fav_before_body": "The current location (plane {0}) is not in the map list and will be lost after teleporting. Save it first?",
    "fav_and_teleport": "Save and teleport", "teleport_anyway": "Teleport anyway",
    "fav_added": "Added to favorites", "plane": "plane {0}",
    "advanced_title": "Advanced", "tab_json": "Raw JSON", "tab_backup": "Backups",
    "json_apply": "Apply", "json_refresh": "Refresh from editor", "json_ok": "Valid JSON",
    "json_error": "Line {0}, column {1}: {2}", "json_not_object": "The top level must be a JSON object",
    "json_applied": "Applied to the editor. Remember to save.", "json_hint": "Edit, click Apply, then save.",
    "backup_empty": "No backups yet (one is made before every save)", "backup_restore": "Restore",
    "backup_open": "Open backup folder", "backup_restored": "Loaded backup {0}. Save to apply.",
    "backup_restore_title": "Restore this backup?",
    "backup_restore_body": "The contents of {0} will be loaded into the editor (not saved yet). Click Save afterwards to write it.",
    "chg_lineup": "Lineup {0}→{1}", "chg_scene": "Map plane {0}→{1}", "chg_skin": "Skins",
    "chg_tb_gender": "Trailblazer gender", "chg_tb_path": "Trailblazer path", "chg_march_path": "March 7th path",
    "chg_other": "Other fields", "chg_none": "No changes",
    "persistent_file": "persistent.json location", "choose_file": "Choose file",
    "shortcut": "Create shortcut", "shortcut_desc": "Add a Starfroster shortcut to the Desktop or Start menu",
    "shortcut_desktop": "Desktop", "shortcut_startmenu": "Start menu",
    "shortcut_done": "Shortcut created", "shortcut_failed": "Could not create the shortcut",
    "pick_persistent_title": "Choose persistent.json",
    "pick_persistent_wrong": "Please choose the file named persistent.json (in ppSR's misc folder)",
    "first_run_title": "Welcome",
    "first_run_body": "First time here: choose the persistent.json you want to edit.\nIt is in the misc folder of ppSR, e.g.\nC:\\StarRail Beta\\ppSR_REL_4.7.5X\\misc\\persistent.json",
    "settings_title": "Settings", "grp_files": "Files", "misc_path": "misc folder",
    "choose_folder": "Choose folder", "misc_invalid": "This folder has no persistent.json",
    "grp_look": "Personalization", "theme": "App theme", "theme_desc": "Light, dark, or follow the system",
    "theme_auto": "Use system setting", "theme_light": "Light", "theme_dark": "Dark",
    "language": "Language", "language_desc": "Takes effect after restarting the editor",
    "language_restart": "Language changed. Restart the editor to apply.",
    "grp_data": "Data", "map_data": "Map data", "map_data_desc": "Source: Escape-penacony · version {0} · updated {1}",
    "map_data_none": "Source: Escape-penacony · not downloaded",
    "char_data": "Character resources", "char_data_desc": "Source: nanoka.cc · data {0} · {1} characters",
    "char_data_none": "Source: nanoka.cc · not downloaded",
    "check_update": "Check for updates", "updated": "Updated", "up_to_date": "Already up to date",
    "clear_icons": "Icon cache cleared", "icon_cache": "Icon cache", "clear": "Clear", "grp_about": "About",
    "about": "About",
    "about_desc": "Starfroster v{1} · ppSR persistent.json editor · data folder: {0}",
    "repo_desc": "Source code, issues and updates",
    "open_data_folder": "Open data folder",
}

PATH_NAMES = {
    "zh": {"Destruction": "毁灭", "Hunt": "巡猎", "Erudition": "智识", "Harmony": "同谐", "Nihility": "虚无",
           "Preservation": "存护", "Abundance": "丰饶", "Remembrance": "记忆", "Elation": "欢愉"},
    "en": {p: p for p in PATHS},
}
ELEMENT_NAMES = {
    "zh": {"Physical": "物理", "Fire": "火", "Ice": "冰", "Thunder": "雷", "Wind": "风", "Quantum": "量子",
           "Imaginary": "虚数"},
    "en": {"Physical": "Physical", "Fire": "Fire", "Ice": "Ice", "Thunder": "Lightning", "Wind": "Wind",
           "Quantum": "Quantum", "Imaginary": "Imaginary"},
}
ELEMENT_COLORS = {"Physical": "#a8a8a8", "Fire": "#f0603c", "Ice": "#58b8e8", "Thunder": "#b46ce6",
                  "Wind": "#4fc596", "Quantum": "#7a6cf0", "Imaginary": "#e6c13c"}


# 皮膚名稱（使用者提供）：皮膚 ID -> (简中, English)
SKIN_NAMES = {
    1100101: ("冬去煦至", "Nascent Spring"),
    1130301: ("雪绽梅笺", "Plumblossom Letter"),
    1131001: ("春日手信", "Spring Missive"),
    1140701: ("幽梦翩跹", "Gossamer Flutter"),
    1140901: ("云边拾暖", "Warm Cotton Skies"),
    1141501: ("「∞」的誓约", "Oath of \"∞\""),
    1150101: ("甜梦电波", "Candy-Coated Waves"),
    1150501: ("月待花时", "Lunar Blossoming"),
}


def skin_name(skin_id: int, fallback: str = "") -> str:
    n = SKIN_NAMES.get(int(skin_id))
    if not n:
        return fallback or str(skin_id)
    return n[1] if LANG == "en" else n[0]


def set_language(lang: str):
    global LANG
    LANG = "en" if lang == "en" else "zh"


def tr(key: str, *args) -> str:
    s = (_EN if LANG == "en" else _ZH).get(key) or _ZH.get(key) or key
    return s.format(*args) if args else s


def path_name(path: str) -> str:
    """path: English path name (Hunt) or base type (Rogue)."""
    p = BASE_TO_PATH.get(path, path)
    return PATH_NAMES[LANG].get(p, path or tr("unknown"))


def element_name(el: str) -> str:
    return ELEMENT_NAMES[LANG].get(el, el or tr("unknown"))


def describe_change(ch: list) -> str:
    k = ch[0]
    if k == "lineup":
        return tr("chg_lineup", ch[1], ch[2])
    if k == "scene":
        return tr("chg_scene", ch[1], ch[2])
    if k in ("tb_gender", "tb_path", "march_path"):
        return f"{tr('chg_' + k)} {ch[1]}→{ch[2]}"
    return tr("chg_" + k)
