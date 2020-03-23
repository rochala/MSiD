package testing;

import algorithms.*;

import java.util.ArrayList;
import java.util.Random;

public class main
{
    public static Random seed = new Random();
    static ArrayList<Integer> randomize_new_array(int size)
    {
        ArrayList<Integer> new_array = new ArrayList<Integer>(size);
        for (int i = 0; i < size; i++) new_array.add(seed.nextInt());
        return new_array;
    }

    static void print_array_out(ArrayList<Integer> array)
    {
        int size = array.size();
        for (int i = 0; i < size; i++)
            System.out.println(array.get(i));

        System.out.println("🧶-----------------------🐈");
    }

    public static void main(String args[])
    {
        ArrayList<Integer> array_for_tests = randomize_new_array(100);

        print_array_out(array_for_tests);
        bubble bubble_sort = new bubble(array_for_tests);
        print_array_out(bubble_sort.sort_out());

        print_array_out(array_for_tests);
        insert insert_sort = new insert(array_for_tests);
        print_array_out(insert_sort.sort_out());
    }
}
