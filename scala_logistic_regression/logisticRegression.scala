package w251.project.logisticregression

import org.apache.spark.SparkContext
import org.apache.spark.SparkContext._
import org.apache.spark.mllib.classification.{LogisticRegressionWithLBFGS, LogisticRegressionModel}
import org.apache.spark.mllib.evaluation.MulticlassMetrics
import org.apache.spark.mllib.regression.LabeledPoint
import org.apache.spark.mllib.linalg.Vectors
import org.apache.spark.mllib.util.MLUtils
import org.apache.spark.SparkConf
import java.io._

object LogisticRegression {
  	def main(args: Array[String]) {
		val sparkConf = new SparkConf().setAppName("LogisticRegression")
		val sc = new SparkContext(sparkConf)

		// Load training and test data CSV
		// Convert data to Double and make tuples- (Label, First N-1 values)

		val rawTrain = sc.textFile("/root/trainData128.txt")
		val rawTest = sc.textFile("/root/testData128.txt")

		val trainData = rawTrain.map(x => x.split(",")).
						map(x => x.map(_.toDouble)).
						map(x => (x.head,Vectors.dense(x.tail)))

		val testData = rawTest.map(x => x.split(",")).
						map(x => (x.head,Vectors.dense(x.tail.map(_.toDouble))))

		//Convert RDD to Labeled Points
		val labeledTrainData = trainData.map(x => LabeledPoint(x._1, x._2))

		// Split data into training (80%) and test (20%).
		val splits = labeledTrainData.randomSplit(Array(0.8, 0.2), seed = 12L)
		val training = splits(0).cache()
		val validation = splits(1)

		// Run training algorithm to build the model
		val model = new LogisticRegressionWithLBFGS().setNumClasses(5).run(training)

		// Compute raw scores on the test set.
		val predictionAndLabels = validation.map { case LabeledPoint(label, features) =>
		  val prediction = model.predict(features)
		  (prediction, label)
		}
        training.unpersist()

 		testData.cache()
		val testPredictions = testData.map(x => (x._1, model.predict(x._2)))
                testData.unpersist()

		val out = testPredictions.collect()

		//Print the results to one file (saveAsText writes to pieces across cluster so this is easier to work with)
		val pw = new PrintWriter(new File("/root/out128.txt"))
		for (i<-out){
			 pw.write(i._1.toString + "\t" + i._2.toString + "\n")
		}
		pw.close

		//Display model metrics
		val metrics = new MulticlassMetrics(predictionAndLabels)
		val precision = metrics.precision
		val f1 = metrics.fMeasure
		val recall = metrics.recall
		val confusionMatrix = metrics.confusionMatrix

		println("Precision = " + precision)
		println("F1 = " + f1)
		println("Recall = " + recall)
		println("\n===Confusion Matrix ===")
		println(confusionMatrix)

		// Save model
		model.save(sc, "/root/logisticRegression128model")

	}
}