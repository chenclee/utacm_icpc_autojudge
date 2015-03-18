import java.io.*;
import java.util.*;
public class Tag {
	static final int[][] deltas = {{0, 1}, {1, 0}, {0, -1}, {-1, 0}};
	public static void main(String[] args) throws Exception {
		Scanner in = new Scanner(System.in);
		int T = in.nextInt();
		while (T-- > 0) {
			int N = in.nextInt();
			int M = in.nextInt();
			int P = in.nextInt();
			boolean[][] passable = new boolean[N][M];
			Player p0 = null;
			Player[] others = new Player[P];
			int[] dirs = new int[P];
			for (int i = 1; i < P; i++) {
				dirs[i] = in.nextInt();
			}
			for (int i = 0; i < N; i++) {
				String line = in.next();
				for (int j = 0; j < M; j++) {
					passable[i][j] = line.charAt(j) != '#';
					if (line.charAt(j) != '.' && line.charAt(j) != '#') {
						if (line.charAt(j) == '0') {
							p0 = new Player(i, j, -1);
						} else {
							int id = (int)(line.charAt(j)-'0');
							others[id] = new Player(i, j, dirs[id]);
						}
					}
				}
			}
			List<Player> remaining = new ArrayList<Player>(P-1);
			for (int i = 1; i < others.length; i++) {
				remaining.add(others[i]);
			}
			int steps;
			//printGrid(0, p0, remaining, passable);
			for (steps = 0; steps < 1800 && remaining.size() > 0; steps++) {

				// move p0
				int closestDist = Integer.MAX_VALUE;
				int closestIndex = -1;
				for (int i = 0; i < remaining.size(); i++) {
					int dist = Math.abs(p0.r - remaining.get(i).r) + Math.abs(p0.c - remaining.get(i).c);
					if (dist < closestDist) {
						closestDist = dist;
						closestIndex = i;
					}
				}
				// take step towards closest index
				int targetR = remaining.get(closestIndex).r;
				int targetC = remaining.get(closestIndex).c;
				int dr = targetR - p0.r;
				int dc = targetC - p0.c;

				//System.out.printf("player 0 moving towards player at (%d, %d). dr = %d, dc = %d\n", targetR, targetC, dr, dc);

				int nextR1, nextC1, nextR2, nextC2;
				// assume moving along row first.
				if (dc > 0) {
					nextC1 = p0.c+1;
				} else if (dc < 0) {
					nextC1 = p0.c-1;
				} else {
					nextC1 = p0.c;
				}
				nextR1 = p0.r;
				if (dr > 0) {
					nextR2 = p0.r+1;
				} else if (dr < 0) {
					nextR2 = p0.r-1;
				} else {
					nextR2 = p0.r;
				}
				nextC2 = p0.c; 
				if (Math.abs(dc) <= Math.abs(dr)) {
					// switch to moving down row first
					int temp = nextC2;
					nextC2 = nextC1;
					nextC1 = temp;
					temp = nextR1;
					nextR1 = nextR2;
					nextR2 = temp;
				}

				//System.out.printf("Player 0 preferred step: (%d, %d), backup: (%d, %d)\n", nextR1, nextC1, nextR2, nextC2);
				
				if (nextR1 >= 0 && nextR1 < N && nextC1 >= 0 && nextC1 < M && passable[nextR1][nextC1]) {
					p0.r = nextR1;
					p0.c = nextC1;
				} else if (nextR2 >= 0 && nextR2 < N && nextC2 >= 0 && nextC2 < M && passable[nextR2][nextC2]) {
					p0.r = nextR2;
					p0.c = nextC2;
				}

				// move other players
				List<Player> nextRemaining = new ArrayList<Player>(remaining.size());
				for (Player p : remaining) {
					// if p0 got you, you're out
					if (p0.r == p.r && p0.c == p.c) continue;
					
					int nextR = p.r + deltas[p.dir][0];
					int nextC = p.c + deltas[p.dir][1];
					if (nextR < 0 || nextR >= N || nextC < 0 || nextC >= M || !passable[nextR][nextC]) {
						//System.out.printf("Player at (%d, %d) rotating\n", p.r, p.c);
						// rotate
						p.dir = (p.dir + 1) % 4;
					} else {
						//System.out.printf("Player at (%d, %d) moving to (%d, %d)\n", p.r, p.c, nextR, nextC);
						p.r = nextR;
						p.c = nextC;
					}

					// if you walked into p0, you're out
					if (p0.r == p.r && p0.c == p.c) continue;
					nextRemaining.add(p);
				}
				remaining = nextRemaining;


				// for debugging, print out grid
				//printGrid(steps + 1, p0, remaining, passable);
			}
			if (remaining.size() > 0) {
				System.out.println("DRAW");
			} else {
				System.out.println(steps);
			}
		}
	}
	static class Player {
		int r;
		int c;
		int dir;
		Player(int r, int c, int dir) {
			this.r = r;
			this.c = c;
			this.dir = dir;
		}
	}
	public static void printGrid(int steps, Player p0, List<Player> remaining, boolean[][] passable) {
		System.out.println("Step " + steps);
		for (int i = 0; i < passable.length; i++) {
			for (int j = 0; j < passable[i].length; j++) {
				boolean isplayer = false;
				if (i == p0.r && j == p0.c) {
					System.out.print('0');
					isplayer = true;
				} else {
					for (Player p : remaining) {
					if (i == p.r && j == p.c) {
							System.out.print('P');
							isplayer = true;
							break;
						}
					}
				}
				if (!isplayer) {
					System.out.print((passable[i][j])? '.' : '#');
				}
			}
			System.out.println();
		}
	}
}
