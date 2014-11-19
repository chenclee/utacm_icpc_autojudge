import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Scanner;

public class wha {
	static ArrayList<String> thing;

	public static void main(String[] args) throws FileNotFoundException {
		
		File file = new File("input1.txt");
		Scanner sc = new Scanner(file);
		int numTimes = sc.nextInt();
		for (int i = 0; i < numTimes; i++) {
			int count = 0;
			sc.nextInt();
			thing = new ArrayList<String>();
			String str = sc.next();
			getPalindromes(str, "");
			for(String wha: thing){
				if(istrue(wha)){
					count++;
				}
			}
			System.out.println(count);
		}

	}

	public static boolean istrue(String str) {
		for (int i = 0; i < str.length(); i++) {
			char c = str.charAt(i);
			char k = str.charAt(str.length() - i - 1);
			if (c != k) {
				return false;
			}
		}
		return true;
	}

	public static void getPalindromes(String str, String prefix) {
		if (str.equals("") && !thing.contains(prefix)) {
			thing.add(prefix);
		} else {
			for (int i = 0; i < str.length(); i++) {
				StringBuilder sb = new StringBuilder(str);

				String wha = prefix;
				wha += str.charAt(i);
				getPalindromes(sb.deleteCharAt(i).toString(), wha);
			}
		}
	}
}
