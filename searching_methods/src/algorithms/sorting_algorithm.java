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

    abstract public void sort_out();
    abstract public void sort_out(ArrayList<Integer> to_be_sorted);
}
