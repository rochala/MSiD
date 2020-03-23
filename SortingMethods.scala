object SortingMethods extends App {

  def quickSort[T <% Ordered[T]](list: List[T]): List[T] =
    list match {
      case Nil => Nil
      case x :: xs =>
        var (before, after) = xs partition (_ < x)
        quickSort(before) ::: x :: quickSort(after)
    }


  def mergeSort[T <% Ordered[T]](list: List[T]): List[T] = {
    def merge(left: List[T], right: List[T]): List[T] = {
      (left, right) match {
        case (_, Nil) => left
        case (Nil, _) => right
        case (lh :: lt, rh :: rt) =>
          if (lh < rh) lh :: merge(lt, right)
          else rh :: merge(left, rt)
      }
    }
    if (list.length / 2 == 0) list
    else if (list.length < 100) {
      quickSort(list)
    } else {
      val (left, right) = list.splitAt(list.length / 2)
      merge(mergeSort(left), mergeSort(right))
    }
  }

  def mergeSortAcc[T](
      inputList: List[T]
  )(implicit order: T => Ordered[T]): List[T] = {
    @scala.annotation.tailrec
    def merge[T](fl: List[T], sl: List[T], acc: List[T] = List())(
        implicit order: T => Ordered[T]
    ): List[T] = {
      (fl, sl) match {
        case (Nil, _) => sl.reverse ::: acc
        case (_, Nil) => fl.reverse ::: acc
        case (fh :: ft, sh :: st) =>
          if (fh.compare(sh) < 0) merge(ft, sl, fh :: acc)
          else merge(fl, st, sh :: acc)
      }
    }
    val n = inputList.length / 2
    if (n == 0) inputList
    else {
      val (left, right) = inputList.splitAt(n)
      merge(mergeSort(left), mergeSort(right)).reverse
    }
  }


  def insertionSort[T](inputList: List[T])(implicit order: T => Ordered[T]): List[T] = {
    inputList.foldLeft(List[T]())((acc, element) => {
      val (left, right) = acc.span(_ < element)
      left ::: element :: right
    })
  }


  var (qS,mS,mSA,iS) = (0.0,0.0,0.0,0.0)
  var actualTime = System.nanoTime()
  val r = new scala.util.Random
  val repeats = 1000
  val toSort = List.fill(1000)(r.nextInt(1000))

  for (i <- 0 to repeats) {
  actualTime = System.nanoTime()
  quickSort(toSort)
  qS += System.nanoTime() - actualTime
  actualTime = System.nanoTime()
  mergeSortAcc(toSort)
  mSA += System.nanoTime() - actualTime
  actualTime = System.nanoTime()
  mergeSort(toSort)
  mS += System.nanoTime() - actualTime
  actualTime = System.nanoTime()
  insertionSort(toSort)
  iS += System.nanoTime() - actualTime
  }

  printf("Quick sort averange time: %5f\n", qS/repeats/1000000000)
  printf("Merge sort averange time: %5f\n", mS/repeats/1000000000)
  printf("Merge sort with accumulator averange time: %5f\n", mSA/repeats/1000000000)
  printf("Insertion Sort averange time: %5f\n", iS/repeats/1000000000)
}
