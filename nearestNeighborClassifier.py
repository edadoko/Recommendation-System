#
#  Nearest Neighbor Classifier


class Classifier:

    def __init__(self, f, dataset):
        self.medianAndDeviation = []
        lines = dataset
        self.format = f
        self.data = []
        for row in dataset:
            ignore = []
            vector = []
            for i in range(len(row)):
                if self.format[i] == 'num':
                    vector.append(float(row[i]))
                elif self.format[i] == 'name':
                    ignore.append(row[i])
                elif self.format[i] == 'class':
                    classification = row[i]
            self.data.append((classification, vector, ignore))
        self.rawData = list(self.data)
        # get length of instance vector
        self.vlen = len(self.data[0][1])
        # now normalize the data
        for i in range(self.vlen):
            self.normalizeColumn(i)

    ##################################################
    ###
    ###  CODE TO COMPUTE THE MODIFIED STANDARD SCORE

    def getMedian(self, alist):
        """return median of alist"""
        if alist == []:
            return []
        blist = sorted(alist)
        length = len(alist)
        if length % 2 == 1:
            # length of list is odd so return middle element
            return blist[int(((length + 1) / 2) -  1)]
        else:
            # length of list is even so compute midpoint
            v1 = blist[int(length / 2)]
            v2 =blist[(int(length / 2) - 1)]
            return (v1 + v2) / 2.0

    def getAbsoluteStandardDeviation(self, alist, median):
        """given alist and median return absolute standard deviation"""
        sum = 0
        for item in alist:
            sum += abs(item - median)
        return sum / len(alist)

    def normalizeColumn(self, columnNumber):
        """given a column number, normalize that column in self.data"""
        # first extract values to list
        col = [v[1][columnNumber] for v in self.data]
        median = self.getMedian(col)
        asd = self.getAbsoluteStandardDeviation(col, median)
        self.medianAndDeviation.append((median, asd))
        for v in self.data:
            v[1][columnNumber] = (v[1][columnNumber] - median) / asd

    def normalizeVector(self, v):
        """We have stored the median and asd for each column.
        We now use them to normalize vector v"""
        vector = list(v)
        for i in range(len(vector)):
            (median, asd) = self.medianAndDeviation[i]
            vector[i] = (vector[i] - median) / asd
        return vector

    ###
    ### END NORMALIZATION
    ##################################################

    def manhattan(self, vector1, vector2):
        """Computes the Manhattan distance."""
        return sum(map(lambda v1, v2: abs(v1 - v2), vector1, vector2))

    def getKey(self, neighbor):
        return neighbor[1]

    def nearestNeighbor(self, itemVector, amount, classified_id):
        """return nearest neighbor to itemVector"""
        neighbors = []
        looper = 0
        for item in self.data:
            if looper != classified_id:
                neighbors.append((looper, self.manhattan(itemVector, item[1]), item[0]))
            looper += 1

        sorted_neighbors = sorted(neighbors, key=self.getKey)
        closest = []
        for i in range(amount):
            closest.append(sorted_neighbors[i])
        return closest

    def classify(self, itemVector, k, classified_id):
        """Return class we think item Vector is in"""
        neighbors = self.nearestNeighbor(self.normalizeVector(itemVector), k, classified_id)
        classes = []

        result = ''
        max_k = 0

        for neighbor in neighbors:
            classes.append(neighbor[2])
            c = classes.count(neighbor[2])
            if c > max_k:
                max_k = c
                result = neighbor[2]

        return result


def test(training_filename, test_filename):
    """Test the classifier on a test set of data"""
    classifier = Classifier(training_filename)
    f = open(test_filename)
    lines = f.readlines()
    f.close()
    numCorrect = 0.0
    for line in lines[1:]:
        data = line.strip().split('\t')
        vector = []
        classInColumn = -1
        for i in range(len(classifier.format)):
              if classifier.format[i] == 'num':
                  vector.append(float(data[i]))
              elif classifier.format[i] == 'class':
                  classInColumn = i
        theClass= classifier.classify(vector)
        prefix = '-'
        if theClass == data[classInColumn]:
            # it is correct
            numCorrect += 1
            prefix = '+'
        print("%s  %12s  %s" % (prefix, theClass, line))
    print("%4.2f%% correct" % (numCorrect * 100/len(lines)))
