from fastapi import APIRouter
from fastapi import Depends
from fastapi import Header
from fastapi import Request
from fastapi import Response

router = APIRouter()


# beatmaps

# @router.post("/web/osu-getbeatmapinfo.php")
# async def get_beatmap_info(): ...


# @router.get("/web/osu-search.php")
# async def search_beatmaps(): ...


# @router.get("/web/osu-search-set.php")
# async def search_beatmap_sets(): ...


# NOTE: technically not /web?
# @router.get("/d/{map_set_id}")
# async def download_beatmap_game_files(): ...


# @router.get("/web/maps/{map_filename}")
# async def get_updated_beatmap(): ...


# @router.get("/web/osu-rate.php")
# async def rate_beatmap(): ...


# NOTE: technically not /web?
# @router.post("/difficulty-rating")
# async def get_difficulty_rating(): ...


# beatmap comments

# @router.post("/web/osu-comment.php")
# async def comment(): ...


# beatmap favourites

# @router.get("/web/osu-addfavourite.php")
# async def add_favourite(): ...


# @router.get("/web/osu-getfavourites.php")
# async def get_favourites(): ...


# scores

# @router.post("/v1/web/osu-submit-modular-selector.php")
# async def submit_modular_selector(): ...


# @router.get("/web/osu-osz2-getscores.php")
# async def get_scores(): ...


# @router.get("/web/osu-getreplay.php")
# async def get_replay(): ...


# screenshots

# @router.post("/v1/web/osu-screenshot.php")
# async def submit_screenshot(): ...


# NOTE: technically not /web?
# @router.get("/ss/{screenshot_id}.{extension}")
# async def get_screenshot(): ...


# errors

# @router.post("/web/osu-error.php")
# async def submit_error(): ...


# messages

# @router.get("/web/osu-markasread.php")
# async def mark_as_read(): ...


# NOTE: technically not /web?
# @router.get("/p/doyoureallywanttoaskpeppy")
# async def do_you_really_want_to_ask_peppy(): ...


# lastfm

# @router.get("/web/lastfm.php")
# async def lastfm(): ...


# seasonal backgrounds

# @router.get("/web/osu-getseasonal.php")
# async def get_seasonal_backgrounds(): ...


# users

# # NOTE: technically not /web?
# @router.post("/users")
# async def create_user(): ...


# @router.get("/web/bancho_connect.php")
# async def bancho_connect(): ...


# osu! game updates

# @router.get("/web/check-updates.php")
# async def check_for_updates(): ...
