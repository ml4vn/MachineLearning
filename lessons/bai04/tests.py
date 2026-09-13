import unittest
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from .algorithms import loss_gradient,gradient_descent
from mlcourse.olist import haversine_km,calendar_late,temporal_split

class RegressionTests(unittest.TestCase):
    def test_one_parameter(self):
        z=np.array([-1.5,-.5,.5,1.5]);y=np.array([-2,-1,1,2])
        _,h=gradient_descent(z[:,None],y,.4,2)
        np.testing.assert_allclose([h[1]['theta_0'],h[1]['loss'],h[2]['theta_0']],[.7,.33125,1.05])
        self.assertAlmostEqual(loss_gradient(z[:,None],y,[1.4])[0],.025)

    def test_gradient_and_simultaneous_step(self):
        X=np.column_stack([np.arange(1,5),np.ones(4)]);y=np.array([3,4,6,7]);th=np.array([.5,1.])
        _,g=loss_gradient(X,y,th)
        fd=[(loss_gradient(X,y,th+e*1e-5)[0]-loss_gradient(X,y,th-e*1e-5)[0])/2e-5 for e in np.eye(2)]
        np.testing.assert_allclose(g,fd,atol=1e-8)
        np.testing.assert_allclose(th-.05*g,[.9,1.1375])

    def test_learning_rate_boundary(self):
        X=np.array([-1.5,-.5,.5,1.5])[:,None];y=np.array([-2,-1,1,2])
        fast,_=gradient_descent(X,y,.8,1);boundary,_=gradient_descent(X,y,1.6,10)
        np.testing.assert_allclose(fast,[1.4]);self.assertAlmostEqual(abs(boundary[0]-1.4),1.4)

    def test_sklearn_ols(self):
        x=np.array([-1.5,-.5,.5,1.5]);X=np.column_stack([np.ones(4),x]);y=np.array([3,4,6,7])
        th,_=gradient_descent(X,y,.4,100)
        m=LinearRegression().fit(x[:,None],y)
        np.testing.assert_allclose(th,[m.intercept_,m.coef_[0]],atol=1e-9)

    def test_geo_and_calendar(self):
        self.assertAlmostEqual(haversine_km(0,0,0,1),111.1950802335,places=6)
        self.assertEqual(haversine_km(12,20,12,20),0)
        got=calendar_late(pd.Series(['2020-01-02 23:59','2020-01-03 00:01']),pd.Series(['2020-01-02','2020-01-02']))
        self.assertEqual(list(got),[0,1])

    def test_label_availability(self):
        d=pd.DataFrame({'order_approved_at':pd.to_datetime(['2017-10-31','2017-10-31','2017-11-01']),
                        'order_delivered_customer_date':pd.to_datetime(['2017-10-31 20:00','2017-11-02 20:00','2017-11-05 20:00'])})
        self.assertEqual(list(temporal_split(d)),['train','outside_window','validation'])

    def test_bad_input(self):
        with self.assertRaises(ValueError): gradient_descent([[1]],[1],eta=0)
        with self.assertRaises(ValueError): loss_gradient([[1]],[np.nan],[0])

if __name__=='__main__': unittest.main()
