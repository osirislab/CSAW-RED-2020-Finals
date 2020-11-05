#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define NSUITS 10
#define MAXINPUTSIZE 1024
#define NAMELENGTH 16

typedef struct _armor{
    char name[NAMELENGTH]; // will read 20 into temp buffer
    int descriptionLength; 
    char * armorDescription;
    //int value;
} armor;

armor * armory[NSUITS];
char nextFreeArmorRackIndex;

void prepareArmory(){
    for (int i = 0; i < NSUITS; i++){
        armory[i] = 0;
    }
    nextFreeArmorRackIndex = 0;
}

int getInput(int length, char * buffer){
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
    return count+1;
}

// second character is for the newline
char getMenuSelection(){
    char input[2]; 
    getInput(2, input);
    return input[0];
}


void checkIn(){
    printf("Some of our owners\' magic items are sentient. What is the name of your armor, so that we could answer any questions it has?\n> ");
    fflush(stdout);
    char tmpName[NAMELENGTH];
    int inputNameLength = getInput(NAMELENGTH, tmpName);

    printf("Please describe your armor:\n> ");
    fflush(stdout);
    char tmpDescription[MAXINPUTSIZE];
    int inputDescriptionLength = getInput(MAXINPUTSIZE, tmpDescription);

    armory[nextFreeArmorRackIndex] = malloc(sizeof(armor));

    memcpy(&armory[nextFreeArmorRackIndex]->name, tmpName, inputNameLength);
    armory[nextFreeArmorRackIndex]->descriptionLength = inputDescriptionLength;

    armory[nextFreeArmorRackIndex]->armorDescription = malloc(inputDescriptionLength);
    memcpy(armory[nextFreeArmorRackIndex]->armorDescription, tmpDescription, inputDescriptionLength);

    printf("Here is a receipt for %s. To reclaim your armor after eight hours, please present me with your ticket number: %d.\n\n", armory[nextFreeArmorRackIndex]->name, nextFreeArmorRackIndex);
    nextFreeArmorRackIndex += 1;
    return;
}

int getClaimNumber(){
    puts("Please enter your claim number.");
    printf("> ");
    fflush(stdout);
    char inputIndex[3];
    read(STDIN_FILENO, inputIndex, 3);
    int index = atoi(inputIndex);
    if((index < 0) || (index > 10) || (index > (nextFreeArmorRackIndex - 1))){
        puts("Error: invalid claim number. Spell will fizzle.");
        exit(0);
    }
    return index;
}

void updateArmor(){
    char nameBuf[20];
    int index = getClaimNumber();
    puts("Okay, I found your armor. Enter the new name:");
    printf("> ");
    fflush(stdout);
    int nameSize = getInput(20, nameBuf);
    if (strlen(nameBuf) < 1){
        printf("Error: you did not enter a name. Spell will fizzle");
        exit(0);
    }
    else if(strlen(nameBuf) > NAMELENGTH){
        memcpy(&armory[index]->name, nameBuf, NAMELENGTH);
    }
    else{
        memcpy(&armory[index]->name, nameBuf, nameSize);
    }
    printf("Thanks! And what is the new description of your armor?\n");
    printf("> ");
    fflush(stdout);
    fgets(armory[index]->armorDescription, armory[index]->descriptionLength, stdin);
    puts("Your information has been updated.\n");
}

void viewArmor(){
    int index = getClaimNumber();
    printf("Grappa brings out your armor named %s for you to view. It looks as follows:\n   %s",armory[index]->name, armory[index]->armorDescription);
    puts("");
}

void handleMenuSelection(char selection){
    if(selection == '1'){
        if(nextFreeArmorRackIndex < NSUITS){
            checkIn();
        }else{
            puts("\"Sorry, our armory is full. Come back another night!\"\n");
            exit(0);
        }
    }
    else if(selection == '2'){
        updateArmor();
    }
    else if(selection == '3'){
        viewArmor();
    }
    else if (selection == '4'){
        puts("   Grappa says, \"So sorry, but we no longer allow guests to retrieve their armor before");
        puts("the spell ends. Last week someone tried to use one of our armor racks after it was free,");
        puts("and it took forever to clean up all the shells. Worse than when Xanathar came over for");
        puts("walnuts, you understand. The establishment apologizes for the inconvenience.\"\n");
    }
    else if(selection == '5'){
        puts("Enjoy your stay at Mordenkainen\'s Magnificent Mansion!\n");
        exit(0);
    }
    else{
        printf("Error: invalid selection.\n");
        exit(0);
    }
    return;
}

void runChallenge(){
    printf("\n");
    prepareArmory();
    while(1){
        puts("What do you wish to do (1-5)?\n");
        puts("1) Check in your armor");
        puts("2) Update the name and description of your armor");
        puts("3) Take a look at your armor");
        puts("4) Retrieve your armor");
        puts("5) Go to the party");
        printf("> ");
        fflush(stdout);
        char selection = getMenuSelection();
        handleMenuSelection(selection);
    }
    return;
}

int main(int argc, char**argv){
    puts("       *** Armor Check ***\n");
    puts("    Welcome to Mordenkainen\'s Magnificent Mansion. I am Grappa,");
    puts("one of my master\'s unseen servants. ");
    puts("    Before your dinner party tonight, please check your armor");
    puts("with me. I see you have multiple members in your party, but that\'s");
    puts("fine because I can accommodate up to ten suits of armor on our racks");
    puts("back here. To retrieve your armor or just change the property description,");
    puts("I\'ll need your name and claim number, so don\'t lose it.");
    puts("    Enjoy your stay! Mordenkainen wants me to remind you that the");
    puts("mansion spell ends after eight hours, so you should finish your business");
    puts("here before then.\n");
    runChallenge();
    return 0;
}