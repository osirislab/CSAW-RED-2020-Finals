#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define NPAGES 60
#define MAXINPUTSIZE 1024
#define NAMELENGTH 16

//int timeRemaining = 20;

typedef struct _spell{
    int nameLength;
    //int incantationLength;
    char * name;
    //char * incantation;
} spell;

spell * spellbook[NPAGES];


int getFreeSpell(){
    for (int i = 0; i < NPAGES; i++){
        if(spellbook[i] == 0){
            return i;
        }
    }
    printf("Error: your spellbook is completely full! It explodes.");
    exit(0);
}


void createSpell(char * name, int length){
    int index = getFreeSpell();
    spellbook[index] = malloc(sizeof(spell));
    //int length = strlen(name);
    //printf("Creating spell named %s with length %d at index %d", name, length, index);
    spellbook[index]->nameLength = length;
    //int incantationLength = strlen(incantation);
    spellbook[index]->name = malloc(length);
    strncpy(spellbook[index]->name, name, length);
    //spellbook[index]->incantation = malloc(incantationLength);
    //strncpy(spellbook[index]->incantation, incantation, incantationLength);
    return;
}

void prepareSpellbook(){
    for (int i = 0; i < NPAGES; i++){
        spellbook[i] = 0;
    }
    createSpell("Jump", 4);//, "puts(\"AAAAAAAAAA!\");");
    createSpell("Alarm", 5);//, "alarm(20);");
    createSpell("Sleep", 5);//, "sleep(20);");
    createSpell("Continual Flame", 15);//, "while (1) printf(\"My grandma types faster than you!\");");
    createSpell("Knock", 5);//, "open(argv[1]);");
    createSpell("Misty Step", 10);//, "jmp *%rax");
    createSpell("Shatter", 7);//, "break;");
    createSpell("Suggestion", 10);//, "sleep(8*60*60);");
    createSpell("Counterspell", 12);//, "signal(SIGINT);");
    createSpell("Banishment", 10);//, "if(0) exit(0);");
    createSpell("Fabricate", 9);//,"memcpy(argv[1],argv[2],40);");
    createSpell("Leomund\'s Secret Chest", 22);//, "push %rax;");
    createSpell("Modify Memory",13);//, "memset(argv[1],argv[2],40);");
    createSpell("Scrying", 7);//, "printf(\"%p\");");
    createSpell("Contact Other Plane", 19);//, "touch(otherplane.c)");
    createSpell("Mordenkainen\'s Magnificent Mansion", 34);//, "ping -c 4 localhost");
    createSpell("Gate", 4);//, "call(runChallenge());");
    //createSpell("Time Stop");//, "if(0) pause();");
}

/*
void roundComplete(){
    timeRemaining -=1;
    if (timeRemaining == 0){
        printf("Oh no! You ran out of time. The extradimensional space collapses! Better luck next time.\n");
        exit(0);
    }else{
        printf("There are %d rounds remaining.\n",timeRemaining);
    }
}
*/

void displaySpells(){
    puts("Your spellbook contains the following spells: \n");
    //spellcounter = 0;
    for (int i = 0; i < NPAGES; i++){
        if(spellbook[i] != 0){
            printf("%d) %s\n", i, spellbook[i]->name);
            //printf("    Spell length: %ld for the strlen but the stored integer is %d \n", strlen(spellbook[i]->name), spellbook[i]->nameLength);//, strlen(spellbook[i]->incantation));
            //printf("%d) Spell: %s\n    %s\n", i, spellbook[i]->name, spellbook[i]->incantation);
            //printf("    Spell length: %ld and incantation length: %ld\n", strlen(spellbook[i]->name), strlen(spellbook[i]->incantation));
            //spellcounter += 1;
        }
    }
    puts("");
    //roundComplete();
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

int getInt(){
    char input[10]; 
    getInput(10, input);
    int result = atoi(input);
    return result;
}

int spellIndexIsValid(int index){
    return(index > -1 && index < NPAGES && spellbook[index]!=0);
}

void castSpell(){
    printf("Enter the index of the spell you wish to cast:\n> ");
    fflush(stdout);
    int index = getInt();
    if (spellIndexIsValid(index)){
        //printf("You cast the %s spell, chanting \'%s!\'\n", spellbook[index]->name, spellbook[index]->incantation);
        printf("You cast the %s spell!\n", spellbook[index]->name);
        puts("The magic fizzles against the anti-magic field, but at least it sounded cool.");
        puts("The spell fades from your spellbook.\n");
        free(spellbook[index]->name);
        //free(spellbook[index]->incantation);
        free(spellbook[index]);
        spellbook[index] = 0;
    }else{
        printf("Incorrect index or the spell there has been cast already!\n");
    }
    //roundComplete();
}

char * combineTwoNames(char* name1, char* name2, int len1, int len2){
    //int len1 = strlen(name1);
    //int len2 = strlen(name2);
    char * newName = malloc(len1+len2);
    strncpy(newName,name1,len1);
    strncpy(&newName[len1],name2,len2);
    //newName[68] = '\x00';
    printf("len1 = %d and len2 = %d", len1, len2);
    newName[(len1+len2)] = '\x00';
    return newName;
}

void combineSpells(){
    printf("Enter the index of the first spell you wish to combine:\n> ");
    fflush(stdout);
    int index1 = getInt();
    printf("Enter the index of the second spell you wish to combine:\n> ");
    fflush(stdout);
    int index2 = getInt();
    if(spellIndexIsValid(index1) && spellIndexIsValid(index2)){
        int len1 = spellbook[index1]->nameLength;
        int len2 = spellbook[index2]->nameLength;
        //char * newName = combineTwoNames(spellbook[index1]->name, spellbook[index2]->name, len1, len2);
        //char * newIncantation = combineTwoFields(spellbook[index1]->incantation, spellbook[index2]->incantation);
        //createSpell(newName, (len1 + len2));
        //free(newName);
        //free(newIncantation);
        int newSpellIndex = getFreeSpell();
        spellbook[newSpellIndex] = malloc(sizeof(spell));
        //printf("Got a free index: %d.",index); // TODO: delete this
        //int length = strlen(name);
        
        spellbook[newSpellIndex]->nameLength = (len1 + len2);
        //int incantationLength = strlen(incantation);
        spellbook[newSpellIndex]->name = malloc(len1 + len2);
        strncpy(spellbook[newSpellIndex]->name, spellbook[index1]->name, len1);
        strncpy(&(spellbook[newSpellIndex]->name[len1]), spellbook[index2]->name, len2);
        spellbook[newSpellIndex]->name[(len1+len2)] = '\x00';
        //printf("In combineSpells: creating spell named %s with length %d at index %d", spellbook[newSpellIndex]->name, (len1 + len2), newSpellIndex);
        //strncpy(spellbook[index]->name, name, length);
        puts("The two spells merge to create a new one on an empty page of your spellbook.\n");
    }else{
        printf("One or more of your spell indices is invalid. Nothing happens.\n");
    }
    //roundComplete();
    return;
}

void modifySpell(){
    printf("Enter the index of the spell you wish to modify:\n> ");
    fflush(stdout);
    int index = getInt();
    if (spellIndexIsValid(index)){
        printf("Old name: %s\n",spellbook[index]->name);
        printf("New name: ");
        fflush(stdout);
        int length = spellbook[index]->nameLength;
        read(STDIN_FILENO, spellbook[index]->name, length);
        spellbook[index]->name[length] = '\x00';
        puts("Spellbook entry updated.\n");
    }else{
        printf("Incorrect index or the spell there has been cast already!\n");
    }
    //roundComplete();
    return;
}


void handleMenuSelection(char selection){
    if(selection == '1'){
        displaySpells();
    }
    else if(selection == '2'){
        combineSpells();
    }
    else if(selection == '3'){
        castSpell();
    }
    else if (selection == '4'){
        modifySpell();
        //roundComplete();
    }
    else{
        printf("Error: invalid selection.\n");
        exit(0);
    }
    return;
}

void runChallenge(){
    printf("\n");
    prepareSpellbook();
    while(1){
        puts("What do you wish to do (1-5)?\n");
        puts("1) View your spells");
        puts("2) Combine two spells");
        puts("3) Cast a spell");
        puts("4) Modify a spell");
        printf("> ");
        fflush(stdout);
        char selection = getMenuSelection();
        handleMenuSelection(selection);
    }
    return;
}

int main(int argc, char**argv){
    puts("********   T H E   T R I A L   ********\n");
    puts("   You have been leveling up your magic throughout the past few months,");
    puts("and the Amethyst Academy brings you before the review board for your");
    puts("final test. Between you and membership in the Council lies a single,");
    puts("eight-hour trial.");
    puts("   The First Mage waves a hand and a gate spell transports you to a");
    puts("dark dimension. You find yourself seated on a rock floating in a void,");
    puts("illuminated by an omnipresent purple light source. Chunks of the rock");
    puts("you are on break off and coalesce again at regular intervals. The air");
    puts("seems to bend and pulse, a sure sign of an active anti-magic field.");
    puts("   Before you on the rock is your spellbook. You sense that the way");
    puts("out of this dimension requires its use somehow, despite the fact that");
    puts("your spells may be ineffectual. Somehow you must engineer an exit, before");
    puts("time runs out!");
    runChallenge();
    return 0;
}