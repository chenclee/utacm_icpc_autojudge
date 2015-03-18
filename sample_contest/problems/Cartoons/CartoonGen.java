import java.io.*;
import java.util.*;

public class CartoonGen {
	public static void main(String[] args) throws Exception {
		int N = Integer.parseInt(args[0]);
		int C = Integer.parseInt(args[1]);
		int S = Integer.parseInt(args[2]);
		int K = Integer.parseInt(args[3]);

		if (S < C) {
			System.out.println("S must be > C");
			return;
		}

		System.out.println(N + " " + C + " " + S + " " + K);
		
		String[][] names = new String[C][N];
		for (int i = 0; i < C; i++) {
			for (int j = 0; j < N; j++) {
				names[i][j] = i+","+j;
			}
		}

		Set<String> fav = new HashSet<String>();
		for (int i = 0; i < C; i++) {
			fav.add(names[i][(int)(Math.random() * N)]);
		}

		while (fav.size() < S) {
			int c = (int)(Math.random() * C);
			int n = (int)(Math.random() * N);
			fav.add(names[c][n]);
		}
		int i = 0;
		for (String s : fav) {
			if (i++ != 0) System.out.print(" ");
			System.out.print(s);
		}
		System.out.println();
		for (int c = 0; c < C; c++) {
			for (int n = 0; n < N; n++) {
				if (n != 0) System.out.print(" ");
				System.out.print(names[c][n]);
			}
			System.out.println();
		}
	}
}
