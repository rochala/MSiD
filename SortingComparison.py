from timeit import default_timer as timer
import random


def insertion_sort(list_to_sort):
    for step in range(1, len(list_to_sort)):
        key = list_to_sort[step]
        j = step - 1
        while j >= 0 and list_to_sort[j] > key:
            list_to_sort[j + 1] = list_to_sort[j]
            j -= 1
        list_to_sort[j + 1] = key


def quick_sort(list_to_sort):
    def partition(sub_list, low, hi):
        pivot = sub_list[(low + hi) // 2]
        left = low
        right = hi
        while left <= right:
            while sub_list[left] < pivot:
                left += 1
            while sub_list[right] > pivot:
                right -= 1
            if left <= right:
                sub_list[left], sub_list[right] = sub_list[right], sub_list[left]
                left += 1
                right -= 1
        return left, right

    def quick_sort_fun(list_to_sort, low, hi):
        if low < hi:
            left, right = partition(list_to_sort, low, hi)
            quick_sort_fun(list_to_sort, low, right)
            quick_sort_fun(list_to_sort, left, hi)

    quick_sort_fun(list_to_sort, 0, len(list_to_sort) - 1)


# shell sort using Knuth's sequence
def shell_sort(list_to_sort):
    def sublist_sort(list_to_sort, start_index, gap):
        for i in range(start_index + gap, len(list_to_sort), gap):
            current_val = list_to_sort[i]
            index = i
            while index >= gap and list_to_sort[index - gap] > current_val:
                list_to_sort[index] = list_to_sort[index - gap]
                index -= gap
            list_to_sort[index] = current_val

    n = len(list_to_sort)
    gap = 1
    while gap < n // 3:
        gap = 3 * gap + 1
    while gap > 0:
        for i in range(gap):
            sublist_sort(list_to_sort, i, gap)
        gap //= 3


def heap_sort(list_to_sort):
    def heapify(list_to_sort, n, i):
        largest_index = i
        left_index = 2 * i + 1
        right_index = 2 * i + 2

        if left_index < n and list_to_sort[i] < list_to_sort[left_index]:
            largest_index = left_index
        if right_index < n and list_to_sort[largest_index] < list_to_sort[right_index]:
            largest_index = right_index
        if largest_index != i:
            list_to_sort[i], list_to_sort[largest_index] = list_to_sort[largest_index], list_to_sort[i]
            heapify(list_to_sort, n, largest_index)

    n = len(list_to_sort)
    for i in range(n, -1, -1):
        heapify(list_to_sort, n, i)
    for i in range(n - 1, 0, -1):
        list_to_sort[i], list_to_sort[0] = list_to_sort[0], list_to_sort[i]
        heapify(list_to_sort, i, 0)


def benchmark_sorting_algorithms(functions_list, list_to_sort):
    print("BENCHMARK START (Times in ms)")

    def benchmark_one_function(function_to_benchmark, *arguments):
        start = timer()
        function_to_benchmark(*arguments)
        end = timer()
        print("{0}: {1}".format(function_to_benchmark.__name__, (end - start) * 1000))

    for function in functions_list:
        benchmark_one_function(function, list_to_sort.copy())


def main():
    list_to_sort_1 = [random.randint(-10000, 10000) for _ in range(10000)]
    list_to_sort_2 = list(range(10000))
    list_to_sort_3 = list(range(10000, 0, -1))

    print("Random list")
    benchmark_sorting_algorithms([quick_sort, heap_sort, shell_sort, insertion_sort], list_to_sort_1)
    print("Increasing list")
    benchmark_sorting_algorithms([quick_sort, heap_sort, shell_sort, insertion_sort], list_to_sort_2)
    print("Decreasing list")
    benchmark_sorting_algorithms([quick_sort, heap_sort, shell_sort, insertion_sort], list_to_sort_3)


if __name__ == "__main__":
    main()
