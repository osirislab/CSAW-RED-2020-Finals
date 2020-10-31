#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define TRUE 1
#define FALSE 0
#define MAXINTLENGTH 5
#define NAMELENGTH 240
#define SIGNATURELENGTH 16 // confirm length of signature

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

char * signInput(){
    puts("Sign input\n");
    return("AAAABBBBCCCCDDDD");
}

_Bool signatureIsValid(){
    return TRUE;
}

void designateField(_Bool isSpellName, char* field){
    //char field[NAMELENGTH];
    char signature[SIGNATURELENGTH];
    puts("Enter the signature for your entry: ");
    getInput(SIGNATURELENGTH, signature);
    if (signatureIsValid(signature)){
        if(isSpellName){
            puts("Enter the name of the spell you wish to cast: ");
        }else{
            puts("Enter the words to be spoken when you cast the spell: ");
        }
        getInput(NAMELENGTH, field);
        if(isSpellName){
        //    memcpy(spellname, field, NAMELENGTH);
            name_registered = TRUE;
        }else{
            //memcpy(invocation, field, NAMELENGTH);
            invocation_registered = TRUE;
        }
    }else{
        puts("Magic field designation failed!\n");
        exit(0);
    }
}

//void designateInvocation(){
//    puts("Designate\n");
//}

void runChallenge(char * invocation, char * spellname){
    puts("   What do you want to do?");
    puts("");
    puts("Options:");
    puts("(1) Sign an input");
    puts("(2) Designate the spell name");
    puts("(3) Designate the spell invocation");
    printf("> ");
    fflush(stdout);
    int selection = getIntClean();

    if(selection == 1){
        signInput();
    }
    else if(selection ==2){
        designateField(1, spellname); // register a spell name
    }
    else if(selection == 3){
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

int main(int argc, char **argv){
    setvbuf(stdout, NULL, _IONBF, 0);
    char invocation[NAMELENGTH];
    char spellname[NAMELENGTH];
    puts("*** Spellbook ***\n");
    puts("   You have encountered an intelligent spellbook");
    puts("that casts its own spells. Can you get it to give");
    puts("you the flag? It\'s a smart spellbook, so it requires all its");
    puts("spell invocations to be signed first to prevent any");
    puts("hocus pocus.");
    puts("   To cast a spell, get a proper RSA signature for both the");
    puts("spell name and spell invocation. The spellbook will immediately");
    puts("cast the spell once you have designate a spell name");
    puts("and invocation with valid signatures.");
    puts("");
    fflush(stdout);
    while(1){
        runChallenge(invocation, spellname);
    }
    printf("\n");
    return 0;
}


