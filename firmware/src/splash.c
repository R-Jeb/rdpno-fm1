/* SPDX-License-Identifier: GPL-3.0-only
 * The start picture (assets/splash_240.png: tools/gen_splash.py -> splash_data.h), drawn line by line as inflate.c
 * gives the pixels: RDPNO's screen saver (rdpno.c), after two minutes without editing.
 *   splash_draw()   the whole screen, ~0.1 s (the sound goes on: it is the audio interrupt's) */
#include "inflate.c"
#include "splash_data.h"

static uint16_t sp_line[2][240];                /* (RAM: the panel's DMA reads it; one fills while one goes out) */
static uint32_t sp_x, sp_y;

static void sp_put(uint8_t b)                   /* two pixels */
{
    uint16_t *l = sp_line[sp_y & 1u];
    l[sp_x++] = SPLASH_PAL[b >> 4];
    l[sp_x++] = SPLASH_PAL[b & 15u];
    if (sp_x == 240u) {
        if (sp_y < 240u) lcd_blit(0, sp_y, 240, 1, l);
        sp_y++;
        sp_x = 0;
    }
}
static void splash_draw(void)
{
    sp_x = sp_y = 0;
    if (inf_run(SPLASH_Z, sizeof SPLASH_Z, sp_put) || sp_y != 240u)
        lcd_fill(0, 0, 240, 240, 0);            /* (broken data: black rather than half a picture) */
}
