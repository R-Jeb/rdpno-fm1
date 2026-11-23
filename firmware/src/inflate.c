/* SPDX-License-Identifier: GPL-3.0-only
 * A small raw-deflate decoder (RFC 1951) that streams: each output byte goes to put(), back references come from a
 * 1 KiB window, so the whole output never has to be in RAM (the start picture: splash.c; compressed with a 1 KiB
 * window, tools/gen_splash.py). After Joergen Ibsen's tinf, written anew.
 *
 *   inf_run(src, n, put)   0 = done, -1 = broken data */

#define INF_WIN 1024u

typedef struct { uint16_t count[16], sym[288]; } inf_tree_t;
static struct {
    const uint8_t *p, *end;
    uint32_t tag, bits;
    uint8_t win[INF_WIN];
    uint32_t pos;
    inf_tree_t lt, dt;
    void (*put)(uint8_t);
} inf;

static uint32_t inf_bit(void)
{
    uint32_t b;
    if (!inf.bits) {
        inf.tag = inf.p < inf.end ? *inf.p++ : 0u;
        inf.bits = 8;
    }
    b = inf.tag & 1u;
    inf.tag >>= 1;
    inf.bits--;
    return b;
}
static uint32_t inf_get(uint32_t n)             /* n bits, the first one lowest */
{
    uint32_t v = 0, i;
    for (i = 0; i < n; i++) v |= inf_bit() << i;
    return v;
}
static void inf_build(inf_tree_t *t, const uint8_t *len, uint32_t n)
{
    uint16_t offs[16];
    uint32_t i, sum = 0;
    for (i = 0; i < 16u; i++) t->count[i] = 0;
    for (i = 0; i < n; i++) t->count[len[i]]++;
    t->count[0] = 0;
    for (i = 0; i < 16u; i++) { offs[i] = (uint16_t)sum; sum += t->count[i]; }
    for (i = 0; i < n; i++)
        if (len[i]) t->sym[offs[len[i]]++] = (uint16_t)i;
}
static int inf_sym(const inf_tree_t *t)         /* one symbol of the canonical code t */
{
    int32_t cur = 0, sum = 0, len = 0;
    do {
        cur = 2 * cur + (int32_t)inf_bit();
        if (++len > 15) return -1;
        sum += t->count[len];
        cur -= t->count[len];
    } while (cur >= 0);
    return t->sym[sum + cur];
}
static void inf_out(uint8_t b)
{
    inf.win[inf.pos++ & (INF_WIN - 1u)] = b;
    inf.put(b);
}
static int inf_block(void)                      /* a Huffman block with inf.lt, inf.dt */
{
    static const uint16_t LBASE[29] = {3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83,
                                       99, 115, 131, 163, 195, 227, 258};
    static const uint8_t LBITS[29] = {0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0};
    static const uint16_t DBASE[30] = {1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025,
                                       1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577};
    static const uint8_t DBITS[30] = {0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12,
                                      12, 13, 13};
    for (;;) {
        int s = inf_sym(&inf.lt);
        uint32_t len, dist;
        if (s < 0) return -1;
        if (s < 256) { inf_out((uint8_t)s); continue; }
        if (s == 256) return 0;
        s -= 257;
        if (s >= 29) return -1;
        len = LBASE[s] + inf_get(LBITS[s]);
        s = inf_sym(&inf.dt);
        if (s < 0 || s >= 30) return -1;
        dist = DBASE[s] + inf_get(DBITS[s]);
        if (dist > INF_WIN || dist > inf.pos) return -1;
        while (len--) inf_out(inf.win[(inf.pos - dist) & (INF_WIN - 1u)]);
    }
}
static int inf_run(const uint8_t *src, uint32_t n, void (*put)(uint8_t))
{
    static const uint8_t ORDER[19] = {16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15};
    uint8_t len[288 + 32];
    uint32_t last, type, i;
    inf.p = src; inf.end = src + n; inf.bits = 0; inf.pos = 0; inf.put = put;
    do {
        last = inf_bit();
        type = inf_get(2);
        if (type == 0) {                        /* stored */
            uint32_t k;
            inf.bits = 0;
            if (inf.end - inf.p < 4) return -1;
            k = (uint32_t)inf.p[0] | (uint32_t)inf.p[1] << 8;
            inf.p += 4;
            if ((uint32_t)(inf.end - inf.p) < k) return -1;
            while (k--) inf_out(*inf.p++);
            continue;
        }
        if (type == 1) {                        /* the fixed codes */
            for (i = 0; i < 288u; i++) len[i] = i < 144u ? 8u : i < 256u ? 9u : i < 280u ? 7u : 8u;
            inf_build(&inf.lt, len, 288);
            for (i = 0; i < 30u; i++) len[i] = 5;
            inf_build(&inf.dt, len, 30);
        } else if (type == 2) {                 /* the codes sent: their lengths, coded too */
            uint32_t hlit = inf_get(5) + 257u, hdist = inf_get(5) + 1u, hclen = inf_get(4) + 4u, k = 0;
            for (i = 0; i < 19u; i++) len[i] = 0;
            for (i = 0; i < hclen; i++) len[ORDER[i]] = (uint8_t)inf_get(3);
            inf_build(&inf.lt, len, 19);
            while (k < hlit + hdist) {
                int s = inf_sym(&inf.lt);
                uint32_t rep, v = 0;
                if (s < 0) return -1;
                if (s < 16) { len[k++] = (uint8_t)s; continue; }
                if (s == 16) { if (!k) return -1; v = len[k - 1]; rep = 3u + inf_get(2); }
                else if (s == 17) rep = 3u + inf_get(3);
                else rep = 11u + inf_get(7);
                if (k + rep > hlit + hdist) return -1;
                while (rep--) len[k++] = (uint8_t)v;
            }
            inf_build(&inf.lt, len, hlit);
            inf_build(&inf.dt, len + hlit, hdist);
        } else {
            return -1;
        }
        if (inf_block()) return -1;
    } while (!last);
    return 0;
}
