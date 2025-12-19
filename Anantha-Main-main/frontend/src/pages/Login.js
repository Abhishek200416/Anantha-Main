import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Mail, Lock, Phone, ArrowLeft } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const Login = () => {
  const navigate = useNavigate();
  const { login, googleLogin, sendPhoneOTP, verifyPhoneOTP } = useAuth();
  const [mode, setMode] = useState('email'); // email, phone, google
  const [loading, setLoading] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  
  const [emailData, setEmailData] = useState({ email: '', password: '' });
  const [phoneData, setPhoneData] = useState({ phone: '', otp: '' });

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await login(emailData);
    
    if (result.success) {
      toast({ title: 'Success', description: 'Logged in successfully!' });
      navigate('/');
    } else {
      toast({ title: 'Error', description: result.error, variant: 'destructive' });
    }
    
    setLoading(false);
  };

  const handleSendOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await sendPhoneOTP(phoneData.phone);
    
    if (result.success) {
      setOtpSent(true);
      toast({ title: 'Success', description: 'OTP sent to your phone!' });
    } else {
      toast({ title: 'Error', description: result.error, variant: 'destructive' });
    }
    
    setLoading(false);
  };

  const handleVerifyOTP = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    const result = await verifyPhoneOTP(phoneData.phone, phoneData.otp);
    
    if (result.success) {
      toast({ title: 'Success', description: 'Logged in successfully!' });
      navigate('/');
    } else {
      toast({ title: 'Error', description: result.error, variant: 'destructive' });
    }
    
    setLoading(false);
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    // Simplified Google login - in production, use proper OAuth flow
    const result = await googleLogin('mock-token');
    
    if (result.success) {
      toast({ title: 'Success', description: 'Logged in with Google!' });
      navigate('/');
    } else {
      toast({ title: 'Error', description: result.error, variant: 'destructive' });
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-white to-red-50 py-12">
      <div className="container mx-auto px-4">
        <button
          onClick={() => navigate('/')}
          className="flex items-center space-x-2 text-gray-600 hover:text-orange-600 mb-6"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Back to Home</span>
        </button>

        <div className="max-w-md mx-auto bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent mb-2">
              Welcome Back!
            </h1>
            <p className="text-gray-600">Login to place your order</p>
          </div>

          {/* Mode Tabs */}
          <div className="flex space-x-2 mb-6 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => { setMode('email'); setOtpSent(false); }}
              className={`flex-1 py-2 rounded-lg font-medium transition-all ${
                mode === 'email'
                  ? 'bg-white shadow text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Email
            </button>
            <button
              onClick={() => { setMode('phone'); setOtpSent(false); }}
              className={`flex-1 py-2 rounded-lg font-medium transition-all ${
                mode === 'phone'
                  ? 'bg-white shadow text-orange-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Phone
            </button>
          </div>

          {/* Email Login */}
          {mode === 'email' && (
            <form onSubmit={handleEmailLogin} className="space-y-4">
              <div>
                <label className="block text-gray-700 font-medium mb-2">Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="email"
                    value={emailData.email}
                    onChange={(e) => setEmailData({ ...emailData, email: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    placeholder="your@email.com"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-gray-700 font-medium mb-2">Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="password"
                    value={emailData.password}
                    onChange={(e) => setEmailData({ ...emailData, password: e.target.value })}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                    placeholder="Enter password"
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50"
              >
                {loading ? 'Logging in...' : 'Login'}
              </button>
            </form>
          )}

          {/* Phone Login */}
          {mode === 'phone' && (
            <div className="space-y-4">
              {!otpSent ? (
                <form onSubmit={handleSendOTP}>
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Phone Number</label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                      <input
                        type="tel"
                        value={phoneData.phone}
                        onChange={(e) => setPhoneData({ ...phoneData, phone: e.target.value })}
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                        placeholder="10-digit mobile number"
                        pattern="[0-9]{10}"
                        required
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full mt-4 bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50"
                  >
                    {loading ? 'Sending OTP...' : 'Send OTP'}
                  </button>
                </form>
              ) : (
                <form onSubmit={handleVerifyOTP}>
                  <div>
                    <label className="block text-gray-700 font-medium mb-2">Enter OTP</label>
                    <input
                      type="text"
                      value={phoneData.otp}
                      onChange={(e) => setPhoneData({ ...phoneData, otp: e.target.value })}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 text-center text-2xl tracking-widest"
                      placeholder="000000"
                      maxLength="6"
                      required
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full mt-4 bg-gradient-to-r from-orange-500 to-red-500 text-white py-3 rounded-lg font-semibold hover:from-orange-600 hover:to-red-600 transition-all disabled:opacity-50"
                  >
                    {loading ? 'Verifying...' : 'Verify OTP'}
                  </button>

                  <button
                    type="button"
                    onClick={() => setOtpSent(false)}
                    className="w-full mt-2 text-orange-600 text-sm hover:underline"
                  >
                    Change phone number
                  </button>
                </form>
              )}
            </div>
          )}

          {/* Divider */}
          <div className="my-6 flex items-center">
            <div className="flex-1 border-t border-gray-300"></div>
            <span className="px-4 text-gray-500 text-sm">OR</span>
            <div className="flex-1 border-t border-gray-300"></div>
          </div>

          {/* Google Login */}
          <button
            onClick={handleGoogleLogin}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 bg-white border-2 border-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-all disabled:opacity-50"
          >
            <svg className="h-5 w-5" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            <span>Continue with Google</span>
          </button>

          {/* Register Link */}
          <p className="mt-6 text-center text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-orange-600 font-semibold hover:underline">
              Register here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;