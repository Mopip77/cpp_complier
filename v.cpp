int x[2][13];

int func(int y){
    int a=x[1][5];
    return a;
}
int main(){
	x[2][7] = 1;
	x[x[1][3][4]][1] = x[2][7];
}
