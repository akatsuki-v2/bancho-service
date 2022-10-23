from datetime import datetime
from enum import IntEnum
from typing import Sequence

from app.api.rest.context import RequestContext
from app.common import logging
from app.models.beatmaps import Beatmap
from app.models.beatmapsets import Beatmapset
from app.models.scores import Score
from app.services.beatmaps_client import BeatmapsClient
from app.services.scores_client import ScoresClient
from app.services.users_client import UsersClient
from fastapi import APIRouter
from fastapi import Depends
from fastapi import Query
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


class LeaderboardType(IntEnum):
    LOCAL = 0
    TOP = 1
    MODS = 2
    FRIENDS = 3
    COUNTRY = 4


class OsuGameMode(IntEnum):
    STANDARD = 0
    TAIKO = 1
    CATCH_THE_BEAT = 2
    MANIA = 3


# TODO: not sure about this
def mode_int_to_string(mode: int) -> str:
    return {
        0: "osu",
        1: "taiko",
        2: "fruits",
        3: "mania",
    }[mode]


def osu_api_ranked_status_to_getscores(status: int) -> int:
    return {
        -2: 0,  # graveyard -> pending
        -1: 0,  # wip -> pending
        0: 0,  # pending -> pending
        1: 2,  # ranked -> ranked
        2: 3,  # approved -> approved
        3: 4,  # qualified -> qualified
        4: 5,  # loved -> loved
    }[status]


# TODO: should these live in serial?

def write_leaderboard_score(score: Score, rank: int) -> bytes:
    timestamp = int(score.created_at.timestamp())
    perfect = "1" if score.perfect else "0"

    return (
        "{score_id}|{username}|{score}|{max_combo}|{count_50s}|{count_100s}|"
        "{count_300s}|{count_misses}|{count_katus}|{count_gekis}|{perfect}|"
        "{mods}|{account_id}|{rank}|{created_at}|{has_replay}"
    ).format(score_id=score.score_id, username=score.username, score=score.score,
             max_combo=score.max_combo, count_50s=score.count_50s,
             count_100s=score.count_100s, count_300s=score.count_300s,
             count_misses=score.count_misses, count_katus=score.count_katus,
             count_gekis=score.count_gekis, perfect=perfect, mods=score.mods,
             account_id=score.account_id, rank=rank, created_at=timestamp,
             has_replay="1").encode() + b"\n"


def write_leaderboard(beatmap: Beatmap, beatmapset: Beatmapset,
                      scores: Sequence[Score],
                      personal_best_score: Score | None) -> bytes:
    response_buffer = bytearray()

    response_buffer += (
        "{ranked_status}|{serv_has_osz2}|{beatmap_id}|{beatmap_set_id}|"
        "{score_count}|{featured_artist_track_id}|{featured_artist_license_text}"
    ).format(ranked_status=osu_api_ranked_status_to_getscores(beatmap.ranked_status),
             serv_has_osz2="0",
             beatmap_id=beatmap.beatmap_id,
             beatmap_set_id=beatmap.set_id,
             score_count=len(scores),
             featured_artist_track_id="0",
             featured_artist_license_text="").encode() + b"\n"

    # TODO: make these real values
    beatmap_offset = 0
    beatmap_rating = 10.0

    # NOTE: `|` is replaced by `\n` by osu! on the client side
    beatmap_name = f'{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]'

    response_buffer += f"{beatmap_offset}\n{beatmap_name}\n{beatmap_rating}\n".encode()

    if personal_best_score is not None:
        response_buffer += write_leaderboard_score(personal_best_score,
                                                   rank=12345)
    else:
        response_buffer += b"\n"

    for idx, score in enumerate(scores):
        response_buffer += write_leaderboard_score(score, rank=idx + 1)

    return bytes(response_buffer)


def create_map_filename(artist: str, title: str, mapper_name: str, version: str) -> str:
    return f"{artist} - {title} ({mapper_name}) [{version}].osu"


@router.get("/v1/web/osu-osz2-getscores.php")
async def get_scores(
    username: str = Query(..., alias="us"),
    password: str = Query(..., alias="ha"),
    requesting_from_editor_song_select: bool = Query(..., alias="s"),
    leaderboard_version: int = Query(..., alias="vv"),
    leaderboard_type: LeaderboardType = Query(..., alias="v"),
    beatmap_md5: str = Query(..., alias="c", min_length=32, max_length=32),
    map_file_name: str = Query(..., alias="f"),
    mode: OsuGameMode = Query(..., alias="m"),
    map_set_id: int = Query(..., alias="i", ge=-1, le=2_147_483_647),
    mods: int = Query(..., alias="mods", ge=0, le=2_147_483_647),
    map_package_hash: str = Query(..., alias="h"),
    aqn_files_found: bool = Query(..., alias="a"),
    ctx: RequestContext = Depends(),
):
    beatmaps_client = BeatmapsClient(ctx)
    scores_client = ScoresClient(ctx)
    users_client = UsersClient(ctx)

    # TODO: validate the user's credentials (username, password)

    mode_str = mode_int_to_string(mode)

    if map_set_id != -1:
        beatmapset = await beatmaps_client.get_beatmapset(map_set_id)
        if beatmapset is None:
            return Response(content=b"-1|false")
    else:
        beatmapset = None

        logging.error("osu! client sent map_set_id=-1, this is not supported")
        return Response(content=b"-1|false")

    # TODO: need some way to fetch_one by md5
    beatmaps = await beatmaps_client.get_beatmaps(md5_hash=beatmap_md5,
                                                  mode=mode_str, page_size=1)
    if beatmaps is None:
        return Response(content=b"-1|false")

    if not beatmaps:
        if beatmapset is None:
            return Response(content=b"-1|false")

        set_beatmaps = await beatmaps_client.get_beatmaps(set_id=beatmapset.beatmapset_id)
        if set_beatmaps is None:
            # TODO is this right?
            return False

        for beatmap in set_beatmaps:
            file_name = create_map_filename(beatmapset.artist,
                                            beatmapset.title,
                                            beatmapset.mapper_name,
                                            beatmap.version)
            if map_file_name == file_name:
                return Response(content=b"1|false")

            return Response(content=b"-1|false")

    if beatmapset is None:
        # we don't have the beatmapset, but we have a map! it has the set id
        beatmapset = await beatmaps_client.get_beatmapset(beatmaps[0].set_id)
        assert beatmapset is not None

    beatmap = beatmaps[0]

    scores = await scores_client.get_scores(beatmap_md5=beatmap_md5,
                                            mode=mode_str, passed=True,
                                            page_size=50)
    if scores is None:
        return Response(content=b"-1|false")

    scores = await scores_client.get_scores(beatmap_md5=beatmap_md5,
                                            account_id=21, mode=mode_str,
                                            passed=True, page_size=50)
    if scores is None:
        return Response(content=b"-1|false")

    personal_best = scores[0] if len(scores) > 0 else None

    response_buffer = write_leaderboard(beatmap, beatmapset,
                                        scores, personal_best)
    return Response(content=response_buffer, status_code=200)


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
