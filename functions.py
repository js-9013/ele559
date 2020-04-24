from zeropdk.layout import layout_waveguide
from zeropdk.layout.waveguide_rounding import *

to_exclude = ['layout_waveguide_from_points']

for name in to_exclude:
    del globals()[name]

def layout_waveguide_from_points(
    cell, layer, points, width, radius, taper_width=None, taper_length=None
):

    assert radius > width, "Please use a radius larger than the pitch"
    points = unique_points(points)

    if len(points) < 2:
        # Nothing to do
        return cell

    # First, get the list of lines and arcs
    try:
        rounded_path = compute_rounded_path(points, radius)
    except Exception as e:
        print("ERROR:", e)
        print("Continuing...")
        dpolygon = layout_waveguide(cell, layer, points, 0.1)
        return dpolygon

    # Taper path if necessary
    if taper_width is not None and taper_length is not None:
        waveguide_path = compute_tapered_path(
            rounded_path, width, taper_width, taper_length
        )
    else:
        waveguide_path = compute_untapered_path(rounded_path, width)

    # creating a single path
    _draw_points = []
    _draw_widths = []
    for element in waveguide_path:
        points, width = element.points, element.widths
        n_points = len(points)
        try:
            if len(width) == n_points:
                _draw_points.extend(points)
                _draw_widths.extend(width)
            elif len(width) == 2:
                _draw_widths.extend(np.linspace(width[0], width[1], n_points))
                _draw_points.extend(points)
            else:
                raise RuntimeError("Internal error detected. Debug please.")
        except TypeError:
            _draw_points.extend(points)
            _draw_widths.extend(np.ones(n_points) * width)

    # deleting repeated points
    _cur_point = None
    _draw_points2 = []
    _draw_widths2 = []
    for p, w in zip(_draw_points, _draw_widths):
        if _cur_point and p == _cur_point:
            continue
        _draw_points2.append(p)
        _draw_widths2.append(w)
        _cur_point = p


    dpolygon = layout_waveguide(cell, layer, _draw_points2, _draw_widths2, smooth=False)

    return dpolygon

def cpwStraight(layout, cell, layer, points, upperWidths, lowerWidths, upperRegion, lowerRegion):
    upperRegion.insert(layout_waveguide(cell, layer, points, upperWidths).to_itype(layout.dbu))
    lowerRegion.insert(layout_waveguide(cell, layer, points, lowerWidths).to_itype(layout.dbu))

    return [upperRegion, lowerRegion] 

def cpwBend(layout, cell, layer, bendPoints, upperWidths, lowerWidths, radius, upperRegion, lowerRegion):
    upperRegion.insert(layout_waveguide_from_points(cell, layer, bendPoints, upperWidths, radius).to_itype(layout.dbu))
    lowerRegion.insert(layout_waveguide_from_points(cell, layer, bendPoints, lowerWidths, radius).to_itype(layout.dbu))

    return [upperRegion, lowerRegion]
