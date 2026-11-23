/* SPDX-License-Identifier: GPL-3.0-only
 * firmware/src/inflate.c against zlib's output (tests/inflate_test.py makes the cases: raw deflate, 1 KiB window,
 * stored, fixed and dynamic blocks). inflate_test COMPRESSED EXPECTED -> 0 = the same bytes */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "inflate.c"
static uint8_t got[1 << 20];
static uint32_t ngot;
static void put(uint8_t b) { if (ngot < sizeof got) got[ngot] = b; ngot++; }
int main(int argc, char **argv)
{
    static uint8_t z[1 << 20], want[1 << 20];
    FILE *f;
    uint32_t nz, nw;
    int r;
    if (argc < 3) return 2;
    f = fopen(argv[1], "rb"); nz = (uint32_t)fread(z, 1, sizeof z, f); fclose(f);
    f = fopen(argv[2], "rb"); nw = (uint32_t)fread(want, 1, sizeof want, f); fclose(f);
    r = inf_run(z, nz, put);
    if (r || ngot != nw || memcmp(got, want, nw)) { printf("%s: FAIL (r %d, %u of %u bytes)\n", argv[1], r, ngot, nw); return 1; }
    printf("%s: %u -> %u bytes, the same\n", argv[1], nz, nw);
    return 0;
}
