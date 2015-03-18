import java.io.*;
import java.util.*;

public class Cartoons {
	public static void main(String[] args) throws Exception {
		Scanner in = new Scanner(System.in);
		int T = in.nextInt();
		while (T-- > 0) {
			int N = in.nextInt();
			int C = in.nextInt();
			int S = in.nextInt();
			int K = in.nextInt();
			Set<String> favs = new HashSet<String>();
			for (int i = 0; i < S; i++) {
				favs.add(in.next());
			}
			boolean[][] isFav = new boolean[C][N];
			for (int i = 0; i < C; i++) {
				for (int j = 0; j < N; j++) {
					isFav[i][j] = favs.contains(in.next());
				}
			}
			int max = 0;
			int[][][] dp = new int[K+1][N+1][C];
			for (int k = K; k > 0; k--) {
				System.out.println("K: " + k);
				for (int n = 0; n < N; n++) {
					for (int c = 0; c < C; c++) {
						if (isFav[c][n]) {
							dp[k][n][c]++;
						}
						System.out.print(dp[k][n][c] + " ");
						max = Math.max(max, dp[k][n][c]);
						// if can change channel, try it
						if (k > 0) {
							for (int i = 0; i < C; i++) {
								if (c == i) continue;
								dp[k-1][n+1][i] = Math.max(dp[k-1][n+1][i], dp[k][n][c]);
							}
						}
						dp[k][n+1][c] = Math.max(dp[k][n+1][c], dp[k][n][c]); // don't change channel
					}
					System.out.println();
				}
			}
			System.out.println(max);
		}
	}
}
