namespace Caribou {
    class Util {
        public static string[] list_to_array (List<string> list) {
            string[] rv = new string[list.length()];
            int i = 0;
            foreach (string v in list) {
                rv[i] = v;
                i++;
            }
            return rv;
        }
    }
}