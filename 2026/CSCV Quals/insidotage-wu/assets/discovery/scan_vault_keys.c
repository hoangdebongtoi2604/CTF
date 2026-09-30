#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <wmmintrin.h>

static inline __m128i spread(__m128i x,__m128i a){
    x=_mm_xor_si128(x,_mm_slli_si128(x,4));
    x=_mm_xor_si128(x,_mm_slli_si128(x,8));
    return _mm_xor_si128(x,a);
}
#define PAIR(i,rc) a=spread(a,_mm_shuffle_epi32(_mm_aeskeygenassist_si128(b,rc),255));rk[i]=a;b=spread(b,_mm_shuffle_epi32(_mm_aeskeygenassist_si128(a,0),170));rk[i+1]=b;
static inline void expand(const unsigned char *key,__m128i *rk){
    __m128i a=_mm_loadu_si128((const __m128i*)key),b=_mm_loadu_si128((const __m128i*)(key+16));
    rk[0]=a;rk[1]=b;
    PAIR(2,1);PAIR(4,2);PAIR(6,4);PAIR(8,8);PAIR(10,16);PAIR(12,32);
    rk[14]=spread(a,_mm_shuffle_epi32(_mm_aeskeygenassist_si128(b,64),255));
}
static inline __m128i enc(__m128i v,__m128i *rk){
    v=_mm_xor_si128(v,rk[0]);
    for(int j=1;j<14;j++)v=_mm_aesenc_si128(v,rk[j]);
    return _mm_aesenclast_si128(v,rk[14]);
}
static void unhex(const char*s,unsigned char*b,int n){for(int i=0;i<n;i++){unsigned x;sscanf(s+2*i,"%2x",&x);b[i]=(unsigned char)x;}}
static void hex(const unsigned char*b,int n){for(int i=0;i<n;i++)printf("%02x",b[i]);}
int main(int argc,char**argv){
    if(argc<7)return 1;
    FILE*f=fopen(argv[1],"rb");if(!f)return 2;
    uint64_t start=strtoull(argv[2],0,10),end=strtoull(argv[3],0,10);
    unsigned char salt[16],cc[16],ct[16],plain[16];
    unhex(argv[4],salt,16);unhex(argv[5],cc,16);unhex(argv[6],ct,16);
    __m128i sv=_mm_loadu_si128((__m128i*)salt),cv=_mm_loadu_si128((__m128i*)cc),ctv=_mm_loadu_si128((__m128i*)ct),rk[15];
    const size_t chunk=16*1024*1024;unsigned char*buf=malloc(chunk+32);
    for(uint64_t base=start;base<end;base+=chunk){
        _fseeki64(f,base,SEEK_SET);size_t n=fread(buf,1,chunk+32,f);
        for(size_t i=0;i+32<=n&&i<chunk&&base+i<end;i+=8){
            if(!*(uint64_t*)(buf+i)||!*(uint64_t*)(buf+i+8)||!*(uint64_t*)(buf+i+16)||!*(uint64_t*)(buf+i+24))continue;
            expand(buf+i,rk);
            __m128i counter=_mm_xor_si128(enc(sv,rk),cv);
            __m128i pv=_mm_xor_si128(enc(counter,rk),ctv);
            _mm_storeu_si128((__m128i*)plain,pv);
            if(plain[0]!='{'||plain[1]!='"')continue;
            int good=1;for(int j=2;j<16;j++)if(plain[j]<32||plain[j]>126)good=0;
            if(good){printf("FOUND offset=%llu key=",(unsigned long long)(base+i));hex(buf+i,32);printf(" counter=");_mm_storeu_si128((__m128i*)plain,counter);hex(plain,16);printf(" plain=");_mm_storeu_si128((__m128i*)plain,pv);fwrite(plain,1,16,stdout);puts("");fflush(stdout);}
        }
        if(((base-start)/chunk)%16==15){printf("progress %llu\n",(unsigned long long)(base+chunk));fflush(stdout);}
        if(n<32)break;
    }
    fclose(f);free(buf);return 0;
}
