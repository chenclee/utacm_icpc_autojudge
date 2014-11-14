#include <iostream>
#include <vector>
#include <algorithm>
#include <cmath>
#include <string>

#define MAX_LEVELS 10

using namespace std;

int bst[(1 << (MAX_LEVELS + 1))];
int inorder[(1 << (MAX_LEVELS + 1))];

void inorderTraversal(int bstIndex, int& inIndex)
{
	if (bstIndex >= (1 << MAX_LEVELS) || bst[bstIndex] <= 0)
	{
		return;
	}

	inorderTraversal(bstIndex * 2 + 1, inIndex);
	inorder[inIndex++] = bst[bstIndex];
	inorderTraversal(bstIndex * 2 + 2, inIndex);
}

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{
		fill(bst, bst + (1 << MAX_LEVELS), 0);
		fill(inorder, inorder + (1 << MAX_LEVELS), 0);

		int height, changes;
		cin >> height >> changes;

		for (int i = 0; i < (1 << height) - 1; ++i)
		{
			cin >> bst[i];
		}

		int index = 0;
		inorderTraversal(0, index);

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

		if (lisSize + changes >= index)
		{
			cout << "YES" << endl;
		}
		else
		{
			cout << "NO" << endl;
		}
	}
}
