#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>

//Prototypes
void _();
void __(int n);
void never();
void gonna(int gate);
void give(int gate1, int gate2);
void you(int c1, int c2, int c3, int c4);
void up();

//Global variables
int fp;
int r;
char content[128];

void _(){

    char buf[100];
    puts("You're no Doom Slayer! I am Vega your glorious overlord.\n");
    fflush(stdout);
    read(0,&buf,0x94);

}

void never() {
    
    printf("Oh snap slayer, Thats the first Doom gate!\n");
    printf("Ok, ok, those pesky demons must be lazy. It's not like you can do it again...\n");
    fp = open("./flagpart_never", O_RDONLY);
    read(fp, content, 128);
    fp = open("./flagpart_gonna", O_RDONLY);
    fflush(stdout);

}

void gonna(int gate) {
    
    // Gaurd
    if(gate != (int)0x12345678){
        printf("Ha ha, you're no match for hell!\n");
        exit(1);
    }
    
    printf("Part 1: ");
    printf("%s", content);
    fflush(stdout);
    printf("\n\n\n\n");
    
    printf("No way!\nNobody gets through a Doom gate that fast!\n");
    printf("That's ok, slayer! Surely you won't get past the marauder...\n");
    
    read(fp,content,128);
    printf("\n\n\nPart 2: ");
    printf("%s", content);
    fflush(stdout);
    printf("\n\n\n\n");

    fp = open("./flagpart_give",O_RDONLY);
    fflush(stdout);

}

void give(int gate1, int gate2) {
    
    // Raise the walls
    if(gate1 != (int)0x6defcab6){
        printf("...slayer, you had me worried there for a second!\n");
        exit(1);
    }

    if(gate2 != (int)0xabcddcba){
        printf("...slayer, you had me worried there for a second!\n");
        exit(1);
    }

    read(fp,content,128);
    printf("Part 3: ");
    printf("%s", content);
    fflush(stdout);
    printf("\n\n\n\n");

    fp = open("./flagpart_you",O_RDONLY);
    printf("Ok Doom slayer, maybe I'll mix it up some!\nTry this next gate on for size!\n");
    fflush(stdout);

}

void you(int c1, int c2, int c3, int c4) {
    char checkMe[4];
    char userChars[4];
    int i;
    checkMe[3] = 'N';
    checkMe[2] = 'U';
    checkMe[1] = 'L';
    checkMe[0] = 'L';
    c1 = c1 & 0x000000ff;
    c2 = c2 & 0x000000ff;
    c3 = c3 & 0x000000ff;
    c4 = c4 & 0x000000ff;
    userChars[0] = (char)(c1 + 1);
    userChars[1] = (char)(c2 + 2);
    userChars[2] = (char)(c3 + 3);
    userChars[3] = (char)(c4 + 4);

    for (i = 0; i< 4; i++){
        if (userChars[i] != checkMe[i]){
            printf("Failed on index: %d",i);
            printf("HAHA! You lose!\n");
            exit(666);
        }
    }
    
    read(fp,content,128);
    printf("Part 4: ");
    printf("%s", content);
    fflush(stdout);
    printf("\n\n\n\n");
    
    printf("Damn, you're good slayer!\n Fine, I got one last trick up my sleeve! Hope you brought the BFG!\n");
    fflush(stdout);

}

void up(int c1, int c2, int c3, int c4, int c5, int c6, int c7) {
    int i; 
    char checkMe[7];
    char userChars[7];
    checkMe[0] = '/';
    checkMe[1] = 'b';
    checkMe[2] = '/';
    checkMe[3] = 't';
    checkMe[4] = 'a';
    checkMe[5] = 'r';
    checkMe[6] = 'd';
    userChars[0] = (char)((c1 ^ 0xffffff00) + 1);
    userChars[1] = (char)((c2 ^ 0xffffff00) + 2);
    userChars[2] = (char)((c3 ^ 0xffffff00) + 3);
    userChars[3] = (char)((c4 ^ 0xffffff00) + 4);
    userChars[4] = (char)((c5 ^ 0xffffff00) + 5);
    userChars[5] = (char)((c6 ^ 0xffffff00) + 6);
    userChars[6] = (char)((c7 ^ 0xffffff00) + 7);

    fp = open("./flagpart_up",O_RDONLY);
    printf("Good luck getting past this one scrub...\n");
    
    for (i = 0; i < 7; i++){
        if (userChars[i] != checkMe[i]){
            printf("Get out of here scrub!\n");
            fflush(stdout);
            exit(666);
        }
    }
    printf("Only the great John Carmack has ever made it here.\n"
            "You have been authorized Doom Slayer! Welcome to hell!\n");
    
    printf("\n\n\nFINAL PART: ");
    read(fp,content,128);
    printf("%s", content);
    fflush(stdout);
    printf("\n\n");
    fflush(stdout);
    exit(1337);

}

int main() {

    printf("This is a restricted area!.. Doom doom doom doom, doom doom doom Doom Doom doom doom, doom doom Doom Doom, doom doom doom D000000m!\n");
    _();
    return 0;

}
