'''Compare crop results with expected output'''

import pytest
import numpy as np
from pathlib import Path
from inspect import currentframe, getframeinfo
from minerva_lib.render import (scale_image_nearest_neighbor,
                                get_region_first_grid,
                                get_optimum_pyramid_level,
                                get_region_grid_shape,
                                transform_coordinates_to_level, select_grids,
                                validate_region_bounds, select_subregion,
                                select_position, composite_subtile,
                                composite_subtiles, extract_subtile)


@pytest.fixture(scope='module')
def dirname():
    filename = getframeinfo(currentframe()).filename
    return Path(filename).resolve().parent.parent


@pytest.fixture(scope='module')
def color_black():
    return np.array([0, 0, 0], dtype=np.float32)


@pytest.fixture(scope='module')
def color_red():
    return np.array([1, 0, 0], dtype=np.float32)


@pytest.fixture(scope='module')
def color_green():
    return np.array([0, 1, 0], dtype=np.float32)


@pytest.fixture(scope='module')
def color_blue():
    return np.array([0, 0, 1], dtype=np.float32)


@pytest.fixture(scope='module')
def color_magenta():
    return np.array([1, 0, 1], dtype=np.float32)


@pytest.fixture(scope='module')
def color_cyan():
    return np.array([0, 1, 1], dtype=np.float32)


@pytest.fixture(scope='module')
def color_orange():
    return np.array([1, .5, 0], dtype=np.float32)


@pytest.fixture(scope='module')
def real_tiles_red_mask(dirname):
    return [
        [
            np.load(Path(dirname, 'data/red/0/0/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/1/0/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/2/0/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/3/0/tile.npy').resolve())
        ],
        [
            np.load(Path(dirname, 'data/red/0/1/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/1/1/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/2/1/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/3/1/tile.npy').resolve())
        ],
        [
            np.load(Path(dirname, 'data/red/0/2/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/1/2/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/2/2/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/3/2/tile.npy').resolve())
        ],
        [
            np.load(Path(dirname, 'data/red/0/3/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/1/3/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/2/3/tile.npy').resolve()),
            np.load(Path(dirname, 'data/red/3/3/tile.npy').resolve())
        ],
    ]


@pytest.fixture(scope='module')
def hd_tiles_green_mask():
    return [
        [
            np.ones((1024, 1024)),
            np.ones((1024, 896))
        ],
        [
            np.ones((56, 1024)),
            np.ones((56, 896))
        ]
    ]


@pytest.fixture(scope='module')
def real_stitched_with_gamma(dirname):
    '''Loads a local red/green composite image from a npy file.

    The red/green composite image originates from a call to the
    blend.composite_channels function with the following arguments:

    [{
        image: # from {URL}/C0-T0-Z0-L0-Y0-X0.png
        color: [1, 0, 0]
        min: 0
        max: 1
    },{
        image: # from {URL}/C1-T0-Z0-L0-Y0-X0.png
        color: [0, 1, 0]
        min: 0.006
        max: 0.024
    }]

    where {URL} is https://s3.amazonaws.com/minerva-test-images/png_tiles
    '''

    return np.load(Path(dirname, 'data/red_green_normalized.npy').resolve())


@pytest.fixture(scope='module')
def real_tiles_green_mask(dirname):
    '''Loads 256x256 px image tiles from npy files.

    The tiles originate from a 1024x1024 px file at {URL}/C1-T0-Z0-L0-Y0-X0.png
    where {URL} is https://s3.amazonaws.com/minerva-test-images/png_tiles.
    '''

    return [
        [
            np.load(Path(dirname, 'data/green/0/0/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/1/0/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/2/0/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/3/0/tile.npy').resolve())
        ],
        [
            np.load(Path(dirname, 'data/green/0/1/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/1/1/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/2/1/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/3/1/tile.npy').resolve())
        ],
        [
            np.load(Path(dirname, 'data/green/0/2/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/1/2/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/2/2/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/3/2/tile.npy').resolve())
        ],
        [
            np.load(Path(dirname, 'data/green/0/3/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/1/3/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/2/3/tile.npy').resolve()),
            np.load(Path(dirname, 'data/green/3/3/tile.npy').resolve())
        ],
    ]


@pytest.fixture(scope='module')
def level0_tiles_green_mask():
    '''Nine 2x2 pixel tiles, green channel.'''

    return [
        [
            np.array([
                [0, 255],
                [0, 0]
            ], dtype=np.uint8),
            np.zeros([2, 2], dtype=np.uint8),
            np.zeros([2, 2], dtype=np.uint8)
        ],
    ] * 3


@pytest.fixture(scope='module')
def level0_tiles_red_mask():
    '''Nine 2x2 pixel tiles, red channel.'''

    return [
        [
            np.array([
                [0, 0],
                [255, 0]
            ], dtype=np.uint8),
            np.zeros([2, 2], dtype=np.uint8),
            np.zeros([2, 2], dtype=np.uint8)
        ],
    ] * 3


@pytest.fixture(scope='module')
def level0_tiles_magenta_mask():
    '''Nine 2x2 pixel tiles, magenta channel.'''

    return [
        [
            np.zeros([2, 2], dtype=np.uint8),
            np.array([
                [0, 255],
                [0, 0]
            ], dtype=np.uint8),
            np.zeros([2, 2], dtype=np.uint8)
        ],
    ] * 3


@pytest.fixture(scope='module')
def level0_tiles_blue_mask():
    '''Nine 2x2 pixel tiles, blue channel.'''

    return [
        [
            np.zeros([2, 2], dtype=np.uint8),
            np.array([
                [0, 0],
                [255, 0]
            ], dtype=np.uint8),
            np.zeros([2, 2], dtype=np.uint8)
        ],
    ] * 3


@pytest.fixture(scope='module')
def level0_tiles_orange_mask():
    '''Nine 2x2 pixel tiles, orange channel.'''

    return [
        [
            np.zeros([2, 2], dtype=np.uint8),
            np.zeros([2, 2], dtype=np.uint8),
            np.array([
                [0, 255],
                [0, 0]
            ], dtype=np.uint8)
        ],
    ] * 3


@pytest.fixture(scope='module')
def level0_tiles_cyan_mask():
    '''Nine 2x2 pixel tiles, cyan channel.'''

    return [
        [
            np.zeros([2, 2], dtype=np.uint8),
            np.zeros([2, 2], dtype=np.uint8),
            np.array([
                [0, 0],
                [255, 0]
            ], dtype=np.uint8)
        ],
    ] * 3


@pytest.fixture(scope='module')
def level0_stitched_green_rgba(color_black, color_green):
    '''One 6x6 pixel green channel stitched from nine tiles.'''

    row_0 = [
        color_black, color_green, color_black,
        color_black, color_black, color_black
    ]
    row_1 = [
        color_black, color_black, color_black,
        color_black, color_black, color_black
    ]
    return np.array([row_0, row_1] * 3, dtype=np.uint8)


@pytest.fixture(scope='module')
def checker_4x4():
    '''One 6x6 pixel image stitched from nine tiles.'''

    return np.array([
        [[0, 0, 0], [1, 1, 1]] * 2,
        [[1, 1, 1], [0, 0, 0]] * 2,
    ] * 2)


@pytest.fixture(scope='module')
def level0_stitched():
    '''One 6x6 pixel image stitched from nine tiles.'''

    return np.array([
        [[0, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 1], [0, 0, 0], [1, 0.5, 0]],
        [[1, 0, 0], [0, 0, 0], [0, 0, 1], [0, 0, 0], [0, 1, 1], [0, 0, 0]],
    ] * 3)


@pytest.fixture(scope='module')
def level1_tile_0_0():
    '''A half-resolution 4x4 tile made using linear interpolation.'''

    # Columns blending Red + Green, Blue + Magenta
    return np.array([
        [[0.25, 0.25, 0], [0.25, 0, 0.5]],
        [[0.25, 0.25, 0], [0.25, 0, 0.5]]
    ])


def test_scale_image_aliasing(checker_4x4):
    '''Test downsampling to 3/4 size without interpolation.'''

    expected = np.array([
        [[0, 0, 0], [0, 0, 0], [1, 1, 1]],
        [[0, 0, 0], [0, 0, 0], [1, 1, 1]],
        [[1, 1, 1], [1, 1, 1], [0, 0, 0]]
    ])

    result = scale_image_nearest_neighbor(checker_4x4, 3 / 4)

    np.testing.assert_allclose(expected, result)


def test_scale_image_asymetry(checker_4x4):
    '''Test downsampling only in y to 3/4 size without interpolation.'''

    expected = np.array([
        [[0, 0, 0], [0, 0, 0], [1, 1, 1]],
        [[1, 1, 1], [1, 1, 1], [0, 0, 0]],
        [[0, 0, 0], [0, 0, 0], [1, 1, 1]],
        [[1, 1, 1], [1, 1, 1], [0, 0, 0]]
    ])

    result = scale_image_nearest_neighbor(checker_4x4, (1, 3 / 4))

    np.testing.assert_allclose(expected, result)


def test_scale_image_invalid_factor(level0_stitched):
    '''Test downsampling level0 to 0% fails.'''

    with pytest.raises(ValueError):
        scale_image_nearest_neighbor(level0_stitched, (0, 0))


def test_get_optimum_pyramid_level_higher():
    '''Test higher resolution than needed for output shape.'''

    expected = 0

    result = get_optimum_pyramid_level((6, 6), 2,
                                       4, True)

    assert expected == result


def test_get_optimum_pyramid_level_lower():
    '''Test lower resolution than needed for output shape'''

    expected = 1

    result = get_optimum_pyramid_level((6, 6), 2,
                                       4, False)

    assert expected == result


def test_transform_coordinates_full_scale():
    '''Test keeping level 0 coordinates unchanged'''

    expected = np.array((6, 6), dtype=np.int64)

    result = transform_coordinates_to_level((6, 6), 0)

    np.testing.assert_array_equal(expected, result)


def test_transform_coordinates_half_scale():
    '''Test scaling level 0 coordinates to level 1 coordinates'''

    expected = np.array((3, 3), dtype=np.int64)

    result = transform_coordinates_to_level((6, 6), 1)

    np.testing.assert_array_equal(expected, result)


def test_select_position_inner_tile():
    '''Test ability to position tile in middle of image.'''

    expected = (2, 2)

    result = select_position((1, 1), (2, 2), (0, 0))

    np.testing.assert_array_equal(expected, result)


def test_get_first_grid_inner_tile():
    '''Ensure correct lower bound for origin after first tile'''

    expected = (1, 1)

    result = get_region_first_grid((2, 2), (2, 2))

    np.testing.assert_array_equal(expected, result)


def test_get_grid_shape_clipped_tiles():
    '''Ensure correct upper bound within level0 shape.'''

    expected = (4, 4)

    result = get_region_grid_shape((2, 2), (3, 3),
                                   (6, 6))

    np.testing.assert_array_equal(expected, result)


def test_validate_region_whole():
    '''Ensure full region is validated.'''

    assert validate_region_bounds(
        (0, 0),
        (6, 6),
        (6, 6)
    )


def test_validate_region_within():
    '''Ensure partial region is validated.'''

    assert validate_region_bounds(
        (1, 0),
        (2, 2),
        (6, 6)
    )


def test_validate_region_exceeds():
    '''Ensure excessively large region is invalidated.'''

    assert not validate_region_bounds(
        (1, 0),
        (6, 6),
        (6, 6)
    )


def test_validate_region_empty():
    '''Ensure empty region is invalidated.'''

    assert not validate_region_bounds(
        (0, 0),
        (0, 0),
        (6, 6)
    )


def test_validate_region_negative():
    '''Ensure negative region is invalidated.'''

    assert not validate_region_bounds(
        (0, -1),
        (2, 2),
        (6, 6)
    )


def test_select_grids_sub_region():
    '''Ensure selection of two tiles for partial region.'''

    expected = [
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 2)
    ]

    result = select_grids(
        (2, 2),
        (3, 3),
        (2, 2)
    )

    np.testing.assert_array_equal(expected, result)


def test_select_grids_full_region():
    '''Ensure selection of all available tiles for full region.'''

    expected = [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]

    result = select_grids((2, 2), (0, 0), (3, 3))

    np.testing.assert_array_equal(expected, result)


def test_select_subregion_ceiling_tile():
    '''Ensure partial tile is selected when full tile unavailable.'''

    expected = [
        (0, 0),
        (1, 1)
    ]

    result = select_subregion((1, 1), (2, 2),
                              (0, 0), (3, 3))

    np.testing.assert_array_equal(expected, result)


def test_extract_subtile_clipped_tile(level1_tile_0_0):
    '''Ensure partial tile is extracted when full tile unnecessary.'''

    expected = np.array([
        [[0.25, 0.25, 0], [0.25, 0, 0.5]]
    ])

    result = extract_subtile((0, 0), (2, 2),
                             (1, 0), (2, 2),
                             level1_tile_0_0)

    np.testing.assert_array_equal(expected, result)


def test_composite_subtile_blending(level0_tiles_red_mask, color_red,
                                    level0_tiles_green_mask, color_green):
    '''Ensure compositing with existing content of stitched region'''

    first_tile = level0_tiles_red_mask[0][0]
    second_tile = level0_tiles_green_mask[0][0]

    expected = np.array([
        [[0, 0, 0], [0, 1, 0]],
        [[1, 0, 0], [0, 0, 0]],
    ])

    result = np.zeros((2, 2) + (3,))

    result = composite_subtile(result, first_tile, (0, 0),
                               color_red, 0, 1)
    result = composite_subtile(result, second_tile, (0, 0),
                               color_green, 0, 1)

    np.testing.assert_array_equal(expected, result)


def test_composite_subtile_cropping(level0_stitched_green_rgba,
                                    level0_tiles_green_mask, color_green):
    '''Test correct cropping of single channel without rendering.'''

    expected = level0_stitched_green_rgba

    tiles = level0_tiles_green_mask
    result = np.zeros((6, 6) + (3,))

    result = composite_subtile(result, tiles[0][0], (0, 0),
                               color_green, 0, 1)
    result = composite_subtile(result, tiles[1][0], (2, 0),
                               color_green, 0, 1)
    result = composite_subtile(result, tiles[2][0], (4, 0),
                               color_green, 0, 1)

    np.testing.assert_array_equal(expected, result)


def test_composite_subtile_square_grid(level0_tiles_green_mask,
                                       level0_tiles_red_mask,
                                       level0_tiles_magenta_mask,
                                       level0_tiles_blue_mask,
                                       level0_tiles_orange_mask,
                                       level0_tiles_cyan_mask,
                                       color_red, color_green, color_blue,
                                       color_magenta, color_cyan, color_orange,
                                       level0_stitched):
    '''Ensure expected rendering of multi-tile multi-channel image.'''

    # Gamma adjusted level0_stitched
    expected = np.array([
        [
            [0,  0,  0], [0,  1,  0], [0,  0,  0],
            [1,  0,  1], [0,  0,  0], [1,  0.72974005, 0]
        ], [
            [1,  0,  0], [0,  0,  0], [0,  0,  1],
            [0,  0,  0], [0,  1,  1], [0,  0,  0]
        ]
    ] * 3)

    result = composite_subtiles([{
        'min': 0,
        'max': 1,
        'grid': (0, 0),
        'image': level0_tiles_green_mask[0][0],
        'color': color_green
    }, {
        'min': 0,
        'max': 1,
        'grid': (1, 0),
        'image': level0_tiles_green_mask[1][0],
        'color': color_green
    }, {
        'min': 0,
        'max': 1,
        'grid': (2, 0),
        'image': level0_tiles_green_mask[2][0],
        'color': color_green
    }, {
        'min': 0,
        'max': 1,
        'grid': (0, 0),
        'image': level0_tiles_red_mask[0][0],
        'color': color_red
    }, {
        'min': 0,
        'max': 1,
        'grid': (1, 0),
        'image': level0_tiles_red_mask[1][0],
        'color': color_red
    }, {
        'min': 0,
        'max': 1,
        'grid': (2, 0),
        'image': level0_tiles_red_mask[2][0],
        'color': color_red
    }, {
        'min': 0,
        'max': 1,
        'grid': (0, 1),
        'image': level0_tiles_magenta_mask[0][1],
        'color': color_magenta
    }, {
        'min': 0,
        'max': 1,
        'grid': (1, 1),
        'image': level0_tiles_magenta_mask[1][1],
        'color': color_magenta
    }, {
        'min': 0,
        'max': 1,
        'grid': (2, 1),
        'image': level0_tiles_magenta_mask[2][1],
        'color': color_magenta
    }, {
        'min': 0,
        'max': 1,
        'grid': (0, 1),
        'image': level0_tiles_blue_mask[0][1],
        'color': color_blue
    }, {
        'min': 0,
        'max': 1,
        'grid': (1, 1),
        'image': level0_tiles_blue_mask[1][1],
        'color': color_blue
    }, {
        'min': 0,
        'max': 1,
        'grid': (2, 1),
        'image': level0_tiles_blue_mask[2][1],
        'color': color_blue
    }, {
        'min': 0,
        'max': 1,
        'grid': (0, 2),
        'image': level0_tiles_orange_mask[0][2],
        'color': color_orange
    }, {
        'min': 0,
        'max': 1,
        'grid': (1, 2),
        'image': level0_tiles_orange_mask[1][2],
        'color': color_orange
    }, {
        'min': 0,
        'max': 1,
        'grid': (2, 2),
        'image': level0_tiles_orange_mask[2][2],
        'color': color_orange
    }, {
        'min': 0,
        'max': 1,
        'grid': (0, 2),
        'image': level0_tiles_cyan_mask[0][2],
        'color': color_cyan
    }, {
        'min': 0,
        'max': 1,
        'grid': (1, 2),
        'image': level0_tiles_cyan_mask[1][2],
        'color': color_cyan
    }, {
        'min': 0,
        'max': 1,
        'grid': (2, 2),
        'image': level0_tiles_cyan_mask[2][2],
        'color': color_cyan
    }], (2, 2), (0, 0), (6, 6))

    np.testing.assert_allclose(expected, result)


def test_composite_subtile_nonsquare(hd_tiles_green_mask, color_green):
    '''Ensure non-square image is stitched correctly with square tiles.'''

    # Gamma correction not needed for fully saturated green channel
    expected = np.ones((1080, 1920, 3)) * [0, 1, 0]

    inputs = []

    for y in range(0, 2):
        for x in range(0, 2):
            inputs += [{
                'min': 0,
                'max': 1,
                'grid': (y, x),
                'image': hd_tiles_green_mask[y][x],
                'color': color_green
            }]

    result = composite_subtiles(inputs, (1024, 1024),
                                (0, 0), (1080, 1920))

    np.testing.assert_allclose(expected, result)


def test_composite_subtiles_real(real_tiles_green_mask, real_tiles_red_mask,
                                 color_red, color_green,
                                 real_stitched_with_gamma):
    '''Ensure 1024 x 1024 image matches image rendered without tiling.'''

    expected = real_stitched_with_gamma

    inputs = []

    for y in range(0, 4):
        for x in range(0, 4):
            inputs += [{
                'min': 0.006,
                'max': 0.024,
                'grid': (y, x),
                'image': real_tiles_green_mask[y][x],
                'color': color_green
            }, {
                'min': 0,
                'max': 1,
                'grid': (y, x),
                'image': real_tiles_red_mask[y][x],
                'color': color_red
            }]

    result = composite_subtiles(inputs, (256, 256),
                                (0, 0), (1024, 1024))

    np.testing.assert_allclose(expected, np.uint8(255*result))