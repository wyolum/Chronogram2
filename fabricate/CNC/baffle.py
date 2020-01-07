from .cnc import MyPath, LASER_THICKNESS

MARGIN = MARGIN = LASER_THICKNESS/2

def create_baffle(baffle_height, 
                  baffle_thickness, 
                  n_notch, 
                  delta,
                  overhang=0,
                  overhang_height=None,
                  overhang_taper=False,
                  margin=MARGIN):
    '''
    delta = DX/DY
    overhang = amount of extra plastic from center of last notch    
    overhang_height = height of overhang.  if None, baffle_height
    margin = extra gap for slots
    '''
    n_notch = n_notch - 1 #### correct for previous interpretation

    if overhang_height is None:
        overhang_height = baffle_height

    p = MyPath()
    p.moveTo(0, 0)
    if overhang > 0:
        p.lineTo(-overhang, 0)
        if overhang_taper:
            p.lineTo(-overhang, overhang_height/2)
        else:
            p.lineTo(-overhang, overhang_height)
        p.lineTo(-baffle_thickness / 2. - margin, overhang_height)
        p.lineTo(-baffle_thickness / 2. - margin,
                  baffle_height / 2 - margin)
    p.lineTo(0, baffle_height / 2 - margin)
    for i in range(n_notch):
        p.lineTo(i * delta + baffle_thickness / 2. + margin,
                  baffle_height / 2 - margin)
        p.lineTo(i * delta + baffle_thickness / 2. + margin,
                  baffle_height)

        p.lineTo((i + 1) * delta - baffle_thickness / 2. - margin,
                  baffle_height)
        p.lineTo((i + 1) * delta - baffle_thickness / 2. - margin,
                  baffle_height / 2 - margin)
        p.lineTo((i + 1) * delta,
                  baffle_height / 2 - margin)
    if overhang > 0:
        p.lineTo(n_notch * delta + baffle_thickness / 2 + margin,
                 baffle_height / 2 - margin)
        p.lineTo(n_notch * delta + baffle_thickness / 2 + margin,
                 overhang_height)
        if overhang_taper:
            p.lineTo(n_notch * delta + overhang, overhang_height/2)
        else:
            p.lineTo(n_notch * delta + overhang, overhang_height)
        p.lineTo(n_notch * delta + overhang, 0)
    p.lineTo(n_notch * delta, 0)
    p.lineTo(0, 0)
    return p

