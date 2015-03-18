import java.io.*;
import java.util.*;

public class JoshBully {
	public static void main(String[] args) throws Exception {
		Scanner in = new Scanner(System.in);
		int T = in.nextInt();
		while (T-- > 0) {
			int D = in.nextInt();
			int L = in.nextInt();
			int[] dp = new int[D+1];
			Arrays.fill(dp, -1);
			dp[D] = 0;
			int max = 0;
			for (int i = D; i >= 0; i--) {
				if (dp[i] == -1) continue;
				// System.out.print(i + ": ");
				max = Math.max(max, dp[i]);
				for (int j = 1; j * j <= i; j++) {
					if (i%j == 0) {
						int other = i/j;
						if (isPrime(j) && i-other-L >= 0) {
							// System.out.print(j + ", ");
							dp[i-other-L] = Math.max(dp[i-other-L], dp[i] + 1);
						}
						if (isPrime(other) && i-j-L >= 0) {
							// System.out.print(other + ", ");
							dp[i-j-L] = Math.max(dp[i-j-L], dp[i] + 1);
						}
					}
				}
				// System.out.println(Arrays.toString(dp));
			}
			System.out.println(max);
		}
	}

	public static boolean isPrime(int p) {
		if (p == 1) return false;
		for (int i = 2; i*i<=p; i++) {
			if (p % i == 0) return false;
		}
		return true;
	}
}
