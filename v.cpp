int fun(int n) {
    int f;
    if (n==1) {
        f = 1;
    }
    else {
        f = fun(n-1) * n;
    }
    return f;
}

int main() {
    float x = 1.1;
    float y = 2.2;
    float z = x + y;
    int a = 4;
    int b;
    b = fun(a);
    return 0;
}