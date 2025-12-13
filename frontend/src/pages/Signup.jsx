import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useState } from 'react';

const schema = yup.object({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required'),
  password: yup.string().min(6, 'Password must be at least 6 characters').required('Password is required'),
  confirmPassword: yup.string()
    .oneOf([yup.ref('password'), null], 'Passwords must match')
    .required('Confirm Password is required'),
}).required();

const Signup = () => {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema)
  });

  const onSubmit = async (data) => {
    setLoading(true);
    try {
      await signup({ name: data.name, email: data.email, password: data.password });
      toast.success('Account created successfully');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-64px)] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 card p-10">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-white">Create an account</h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="rounded-md shadow-sm -space-y-px">
             <div className="mb-4">
              <label htmlFor="name" className="sr-only">Name</label>
              <input
                id="name"
                type="text"
                {...register('name')}
                className={`appearance-none rounded relative block w-full px-3 py-2 border ${errors.name ? 'border-red-500' : 'border-gray-600'} placeholder-gray-400 bg-gray-700/50 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Full Name"
              />
              {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name.message}</p>}
            </div>
            <div className="mb-4">
              <label htmlFor="email-address" className="sr-only">Email address</label>
              <input
                id="email-address"
                type="email"
                {...register('email')}
                className={`appearance-none rounded relative block w-full px-3 py-2 border ${errors.email ? 'border-red-500' : 'border-gray-600'} placeholder-gray-400 bg-gray-700/50 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Email address"
              />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
            </div>
            <div className="mb-4">
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                type="password"
                {...register('password')}
                className={`appearance-none rounded relative block w-full px-3 py-2 border ${errors.password ? 'border-red-500' : 'border-gray-600'} placeholder-gray-400 bg-gray-700/50 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Password"
              />
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
            </div>
             <div>
              <label htmlFor="confirmPassword" className="sr-only">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                {...register('confirmPassword')}
                className={`appearance-none rounded relative block w-full px-3 py-2 border ${errors.confirmPassword ? 'border-red-500' : 'border-gray-600'} placeholder-gray-400 bg-gray-700/50 text-white focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm`}
                placeholder="Confirm Password"
              />
              {errors.confirmPassword && <p className="text-red-500 text-xs mt-1">{errors.confirmPassword.message}</p>}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex justify-center py-2 px-4 shadow-sm text-sm font-medium rounded-md text-white disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>
           <div className="text-center text-sm">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link to="/login" className="font-medium text-indigo-400 hover:text-indigo-300">
                Log in
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Signup;
