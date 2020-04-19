package testing;

import algorithms.*;

import java.util.ArrayList;
import java.util.Random;

public class main
{
    static Random seed = new Random();
    static ArrayList<Integer> randomize_new_array(int size)
    {
        ArrayList<Integer> new_array = new ArrayList<Integer>(size);
        for (int i = 0; i < size; i++) new_array.add(seed.nextInt());
        return new_array;
    }

    static void print_array_out(ArrayList<Integer> array)
    {
        for (Integer integer : array)
            System.out.println(integer);

        System.out.println("🧶-----------------------🐈");
    }

    static float estimate_sorting_duration(sorting_algorithm algorithm, ArrayList<ArrayList<Integer>> arrays)
    {
        if(arrays.isEmpty()) return -1;

        long start_time = System.currentTimeMillis();

        for (ArrayList<Integer> array : arrays)
            algorithm.sort_out(array);

        return (float)(System.currentTimeMillis() - start_time) / arrays.size();
    }

    public static void main(String args[])
    {
        int number_of_tests = 10, test_size = 10000;
        ArrayList<ArrayList<Integer>> set_of_tests = new ArrayList<ArrayList<Integer>>(number_of_tests);

        for (int i = 0; i < number_of_tests; i++)
            set_of_tests.add(randomize_new_array(test_size));

        bubble bubble_sort = new bubble();
        insert insert_sort = new insert();
        select select_sort = new select();
        quick quick_sort = new quick();

        System.out.println(estimate_sorting_duration(bubble_sort, set_of_tests) + " [ms]");
        System.out.println(estimate_sorting_duration(insert_sort, set_of_tests) + " [ms]");
        System.out.println(estimate_sorting_duration(select_sort, set_of_tests) + " [ms]");
        System.out.println(estimate_sorting_duration(quick_sort, set_of_tests) + " [ms]");
    }
}
