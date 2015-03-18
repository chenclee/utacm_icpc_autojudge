import java.io.*;
import java.util.*;

public class MarbleRun {
	public static void main(String[] args) throws Exception {
		Scanner in = new Scanner(System.in);
		int T = in.nextInt();
		while (T-- > 0) {
			int N = in.nextInt();
			in.nextLine();
			int[][] input = new int[N][];
			for (int i = 0; i < N; i++) {
				String[] vals = in.nextLine().split(" ");
				input[i] = new int[vals.length];
				for (int j = 0; j < vals.length; j++) {
					input[i][j] = Integer.parseInt(vals[j]);
				}
			}
			System.out.println(calc(0, input));
		}
	}
	public static int calc(int cur, int[][] vals) {
		int max = 0;
		for (int i = 1; i < vals[cur].length; i++) {
			max = Math.max(max, calc(vals[cur][i], vals));
		}
		return max + vals[cur][0];
	}
}
