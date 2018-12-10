int x = 3;

int func1(int vv){
	vv = vv * 3;
	return vv;
}

int main(){
	int c,y = (3 + 5) * func1(x);

	int num = 0;

	while (y >= 0){
		if (y > 10){
			y = y - 4;
		}else{
			y = y - 2;
		}
	}
}