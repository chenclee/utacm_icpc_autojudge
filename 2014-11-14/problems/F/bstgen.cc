#include <iostream>
#include <algorithm>
#include <cstdlib>

using namespace std;

void randomGen(int* tree, int n, int node)
{
	if (node >= n)
	{
		return;
	}

	tree[node] = (1 + rand() % 1000000);

	if (rand() % 2 || rand() % 2)
	{
		randomGen(tree, n, node * 2 + 1);
	}

	if (rand() % 2 || rand() % 2)
	{
		randomGen(tree, n, node * 2 + 2);
	}
}

void inorderTrav(int* tree, int n, int node, int* a, int& i)
{
	if (n <= node)
	{
		return;
	}

	inorderTrav(tree, n, node * 2 + 1, a, i);
	a[i++] = tree[node];
	inorderTrav(tree, n, node * 2 + 2, a, i);
}

int main()
{
	srand(time(0));

	int tests;
	cin >> tests;

	cout << tests << endl;

	while (tests-- > 0)
	{
		int h = (1 + (rand() % 10));
		int size = (1 << h) - 1;
		int data[size];
		fill(data, data + size, 0);
		randomGen(data, size, 0);

		int inorder[size];
		int index = 0;
		inorderTrav(data, size, 0, inorder, index);

		int lisSize = 0;
		int lis[index];
		fill(lis, lis + index, 1);

		for (int i = 1; i < index; ++i)
		{
			for (int j = i - 1; j >= 0; --j)
			{
				if (inorder[j] < inorder[i])
				{
					lis[i] = max(lis[i], 1 + lis[j]);
				}
			}

			lisSize = max(lisSize, lis[i]);
		}

		if (rand() % 2)
		{
			cout << h << " " << (index - lisSize) << endl;
		}
		else
		{
			cout << h << " " << (rand() % index) << endl;
		}

		for (int i = 0; i < size; ++i)
		{
			cout << data[i];

			if (i != size - 1)
			{
				cout << " ";
			}
		}
		cout << endl;
	}
}
