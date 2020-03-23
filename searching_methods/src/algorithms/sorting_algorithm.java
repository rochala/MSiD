package algorithms;

import java.util.ArrayList;

public abstract class sorting_algorithm
{
    ArrayList<Integer> to_be_sorted;

    public sorting_algorithm(ArrayList<Integer> to_be_sorted)
    {
        this.to_be_sorted = to_be_sorted;
    }
    public void change_source(ArrayList<Integer> to_be_sorted)
    {
        this.to_be_sorted = to_be_sorted;
    }

    void swap(int index_1, int index_2)
    {
        int temp = to_be_sorted.get(index_1);
        to_be_sorted.set(index_1, to_be_sorted.get(index_2));
        to_be_sorted.set(index_2, temp);
    }
    public ArrayList<Integer> sort_out(ArrayList<Integer> to_be_sorted)
    {
        this.to_be_sorted = to_be_sorted;
        return sort_out();
    }

    abstract public ArrayList<Integer> sort_out();
}
