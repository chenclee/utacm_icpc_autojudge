#include <iostream>
#include <algorithm>
#include <vector>
#include <map>
#include <queue>
#include <set>

#define MAX_SIZE 100
#define NORTH 0
#define EAST 1
#define SOUTH 2
#define WEST 3

using namespace std;

int steps[4][2] = {
	{-1, 0}, {0, 1}, {1, 0}, {0, -1}
};

int moveSteps[12][2] = {
	{1, 0}, {2, 0},
	{-1, 0}, {-2, 0},
	{0, 1}, {0, 2},
	{0, -1}, {0, -2},
	{1, 1}, {-1, -1},
	{1, -1}, {-1, 1}
};

char grid[MAX_SIZE][MAX_SIZE];
bool danger[MAX_SIZE][MAX_SIZE];

struct laser
{
	int row, col, direction;
};

bool valid(int r, int c, int n, int m)
{
	return r >= 0 && c >= 0 && r < n && c < m;
}

void fillLaser(int n, int m, laser& l)
{
	int r = l.row;
	int c = l.col;
	int dir = l.direction;

	while (valid(r, c, n, m))
	{
		danger[r][c] = true;

		if (grid[r][c] == '/')
		{
			if (dir == NORTH)
			{
				dir = EAST;
			}
			else if (dir == EAST)
			{
				dir = NORTH;
			}
			else if (dir == SOUTH)
			{
				dir = WEST;
			}
			else
			{
				dir = SOUTH;
			}
		}
		else if (grid[r][c] == '\\')
		{
			if (dir == NORTH)
			{
				dir = WEST;
			}
			else if (dir == EAST)
			{
				dir = SOUTH;
			}
			else if (dir == SOUTH)
			{
				dir = EAST;
			}
			else
			{
				dir = NORTH;
			}
		}
		else if (grid[r][c] == '|')
		{
			if (dir == WEST || dir == EAST)
			{
				break;
			}
		}
		else if (grid[r][c] == '-')
		{
			if (dir == NORTH || dir == SOUTH)
			{
				break;
			}
		}

		r += steps[dir][0];
		c += steps[dir][1];
	}
}

void fillLasers(int n, int m, vector<laser>& lasers)
{
	for (int i = 0; i < lasers.size(); ++i)
	{
		fillLaser(n, m, lasers[i]);
	}
}

void assignNeighbors(int n, int m, map<pair<int, int>, vector<pair<int, int> > >& neighbors)
{
	for (int i = 0; i < n; ++i)
	{
		for (int j = 0; j < m; ++j)
		{
			for (int k = 0; k < 12; ++k)
			{
				int r = i + moveSteps[k][0];
				int c = j + moveSteps[k][1];

				if (valid(r, c, n, m) && !danger[r][c])
				{
					neighbors[pair<int, int>(i, j)].push_back(pair<int, int>(r, c));
				}
			}
		}
	}
}

bool success(int r, int c, int n, int m)
{
	map<pair<int, int>, vector<pair<int, int> > > neighbors;
	set<pair<int, int> > visited;
	assignNeighbors(n, m, neighbors);

	queue<pair<int, int> > q;
	q.push(pair<int, int>(r, c));
	visited.insert(pair<int, int>(r, c));

	while (!q.empty())
	{
		pair<int, int> p = q.front();
		q.pop();

		int r = p.first;
		int c = p.second;

		if (grid[r][c] == '*')
		{
			return true;
		}

		for (int i = 0; i < neighbors[p].size(); ++i)
		{
			int newR = neighbors[p][i].first;
			int newC = neighbors[p][i].second;

			if (valid(r, c, n, m) && visited.find(neighbors[p][i]) == visited.end())
			{
				visited.insert(neighbors[p][i]);
				q.push(neighbors[p][i]);
			}
		}
	}

	return false;
}

int main()
{
	int tests;
	cin >> tests;

	while (tests-- > 0)
	{
		int n, m;
		cin >> n >> m;

		bool danger[n][m];
		for (int i = 0; i < n; ++i)
		{
			fill(grid[i], grid[i] + m, false);
		}

		vector<laser> lasers;
		int startRow = -1, startCol = -1;
		for (int i = 0; i < n; ++i)
		{
			for (int j = 0; j < m; ++j)
			{
				cin >> grid[i][j];

				if (grid[i][j] == 'R')
				{
					startRow = i;
					startCol = j;
				}

				danger[i][j] = (grid[i][j] != '.' && grid[i][j] != 'R' && grid[i][j] != '*');

				if (grid[i][j] != 'N' && grid[i][j] != 'E' && grid[i][j] != 'S' && grid[i][j] != 'W')
				{
					continue;
				}

				laser l;

				l.row = i;
				l.col = j;

				if (grid[i][j] == 'N')
				{
					l.direction = NORTH;
				}
				
				if (grid[i][j] == 'E')
				{
					l.direction = EAST;
				}
				
				if (grid[i][j] == 'S')
				{
					l.direction = SOUTH;
				}
				
				if (grid[i][j] == 'W')
				{
					l.direction = WEST;
				}

				lasers.push_back(l);
			}
		}

		fillLasers(n, m, lasers);

		if (success(startRow, startCol, n, m))
		{
			cout << "YES" << endl;
		}
		else
		{
			cout << "NO" << endl;
		}
	}
}
