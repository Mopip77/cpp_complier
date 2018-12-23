int main() {
    int arr1[3][4];
    int arr2[4][3];
    int arr3[3][3];

    int i = 0;

    i = 0;
    while(i<3) {
        int x = 0;
        while(x<4) {
            arr1[i][x] = i + x;
            x = x + 1;
        }
        i = i + 1;
    }

    i = 0;
    while(i<4) {
        int x = 0;
        while(x<3) {
            arr2[i][x] = i * x;
            x = x + 1;
        }
        i = i + 1;
    }

    i = 0;
    while(i<3) {
        int j = 0;
        while(j<3) {
            int sum = 0;
            int k = 0;
            while(k<4) {
                sum = sum + arr1[i][k] * arr2[k][j];
                k = k + 1;
            }
            arr3[i][j] = sum;
            j = j + 1;
        }
        i = i + 1;
    }

    i = 0;
    while(i<3) {
	int j = 0;
	while(j<3){
		print(arr3[i][j]);
                j = j + 1;
	}
	i = i + 1;
}
    //0 14 28 (0 0E 1C)
    //0 20 40 (0 14 28)
    //0 26 52 (0 1A 34)
    return 0;

}
