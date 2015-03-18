import java.io.*;
import java.util.*;

public class TagGen {
	public static void main(String[] args) throws Exception {
		int N = Integer.parseInt(args[0]);
		int M = Integer.parseInt(args[1]);
		int P = Integer.parseInt(args[2]);
		assert P < 10;
		int numObstacles = (int)(Double.parseDouble(args[3]) * N * M);
		assert numObstacles + P <= N*M;

		char[][] out = new char[N][M];
		for (int i = 0; i < N; i++) {
			for (int j = 0; j < M; j++) {
				out[i][j] = '.';
			}
		}
		for (int i = 0; i < numObstacles; i++) {
			int r, c;
			do {
				r = (int)(Math.random() * N);
				c = (int)(Math.random() * M);
			} while (out[r][c] != '.');
			out[r][c] = '#';
		}
		for (int i = 0; i < P; i++) {
			int r, c;
			do {
				r = (int)(Math.random() * N);
				c = (int)(Math.random() * M);
			} while (out[r][c] != '.');
			out[r][c] = (char)('0' + i);
		}
		System.out.println(N + " " + M + " " + P);
		for (int i = 0; i < P-1; i++) {
			if (i != 0) System.out.print(" ");
			System.out.print((int)(Math.random() * 4));
		}
		System.out.println();
		for (int i = 0; i < N; i++) {
			for (int j = 0; j < M; j++) {
				System.out.print(out[i][j]);
			}
			System.out.println();
		}
	}
}
