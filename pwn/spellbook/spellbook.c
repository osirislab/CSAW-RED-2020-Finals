#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define TRUE 1
#define FALSE 0
#define MAXINTLENGTH 5
#define NAMELENGTH 40
#define INVOCATIONLENGTH 1200
//#define SIGNATURELENGTH 16 // confirm length of signature

_Bool invocation_registered = FALSE;
_Bool name_registered = FALSE;



void getInput(int length, char * buffer){
    memset(buffer, 0, length);
    int count = 0;
    char c;
    while((c = getchar()) != '\n' && !feof(stdin)){
        if(count < (length-1)){
            buffer[count] = c;
            count++;
        }
    }
    buffer[count] = '\x00'; 
}

int getIntClean(){
    char input[MAXINTLENGTH]; 
    getInput(MAXINTLENGTH, input);
    return atoi(input);
}

//char * signInput(){
//    puts("Sign input\n");
//    return("AAAABBBBCCCCDDDD");
//}

//_Bool signatureIsValid(){
//    return TRUE;
//}

void designateField(_Bool isSpellName, char* field){
    //char field[NAMELENGTH];
    //char signature[SIGNATURELENGTH];
    //puts("Enter the signature for your entry: ");
    //getInput(SIGNATURELENGTH, signature);
    if(isSpellName){
        puts("Enter the name of the spell you wish to cast: ");
        getInput(NAMELENGTH, field);
        name_registered=TRUE;
    }else{
        puts("Enter the words to be spoken when you cast the spell: ");
        getInput(INVOCATIONLENGTH, field);
        invocation_registered=TRUE;
    }
    //getInput(NAMELENGTH, field);
    //if(isSpellName){
    //    memcpy(spellname, field, NAMELENGTH);
    //    name_registered = TRUE;
    //}else{
        //memcpy(invocation, field, NAMELENGTH);
    //    invocation_registered = TRUE;
    //}
    return;
}

//void designateInvocation(){
//    puts("Designate\n");
//}

void runRitualCasting(char * invocation, char * spellname){
    puts("   What do you want to do?");
    puts("");
    puts("Options:");
    puts("(1) Designate the spell name");
    puts("(2) Designate the spell invocation");
    printf("> ");
    fflush(stdout);
    int selection = getIntClean();

    if(selection ==1){
        designateField(1, spellname); // register a spell name
    }
    else if(selection == 2){
        designateField(0, invocation); // register an invocation
    }
    else if(selection == 1337){
        puts("");
        puts("Casting the Scrying spell to display spell name information for debugging purposes.\n");
        puts("(Remove this menu option before deploying application)\n");
        printf("Spell name registry information is at %p and has value %d\n", &name_registered, name_registered);
        if(name_registered){
            printf(spellname);
        }
        puts("");
        fflush(stdout);
    }
    else{
        printf("Illegal selection.");
        fflush(stdout);
        exit(0);
    }
    if(name_registered && invocation_registered){
        printf("Casting the %s spell...", spellname);
        printf(invocation);
        exit(0);
    }
    return;
}

//void runGame(){
//    puts("--- CSAW FINALS REGISTRATION ---");
//    while(1){
//        runMenu();
//    }
//    return;
//}

int accessSpellbook(){
    char invocation[INVOCATIONLENGTH];
    char spellname[NAMELENGTH];
    puts("*** Spellbook ***\n");
    puts("   You have encountered an intelligent spellbook");
    puts("that casts its own spells. Can you get it to give");
    puts("you the flag?");
    puts("");
    fflush(stdout);
    while(1){
        runRitualCasting(invocation, spellname);
    }
    printf("\n");
    return 0;
}

/*
int accessRitualChamber(){
    accessSpellbook();
    return 0;
}

int accessPalace(){
    accessRitualChamber();
    return 0;
}

int accessCapitolCity(){
    accessPalace();
    return 0;
}

int accessFloatingContinent(){
    accessCapitolCity();
    return 0;
}

int accessPocketDimension(){
    accessFloatingContinent();
    return 0;
}*/

int main(int argc, char **argv){
    setvbuf(stdout, NULL, _IONBF, 0);
    accessSpellbook();
    return 0;
}


