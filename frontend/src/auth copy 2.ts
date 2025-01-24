import NextAuth from 'next-auth';
import Credentials from 'next-auth/providers/credentials';
import type { Provider } from 'next-auth/providers';

const providers: Provider[] = [
  Credentials({
    credentials: {
      email: { label: 'Email Address', type: 'email' },
      password: { label: 'Password', type: 'password' },
    },
    async authorize(credentials) {
      try {
        const res = await fetch('http://localhost:3000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: credentials?.email,
            password: credentials?.password,
          }),
        });

        if (!res.ok) {
          throw new Error('Invalid email or password');
        }

        const data = await res.json();

        // Map the response data to the user object
        if (data?.user) {
          return {
            id: data.user.id,
            name: data.user.name,
            email: data.user.email,
            role: data.user.role, // Optional: depends on your API response
          };
        }

        return null; // Return null if the login is invalid
      } catch (error) {
        console.error('Login failed:', error);
        throw new Error('Login failed, please try again');
      }
    },
  }),
];

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers,
  secret: process.env.AUTH_SECRET,
  pages: {
    signIn: '/auth/signin',
  },
  callbacks: {
    session({ session, token }) {
      // Add user id and role to the session
      if (token) {
        session.user.id = token.id;
        session.user.role = token.role;
      }
      return session;
    },
    jwt({ token, user }) {
      // Persist user id and role to the token
      if (user) {
        token.id = user.id;
        token.role = user.role;
      }
      return token;
    },
    async authorized({ auth: session, request: { nextUrl } }) {
      const isLoggedIn = !!session?.user;
      const isPublicPage = nextUrl.pathname.startsWith('/public');

      if (isPublicPage || isLoggedIn) {
        return true;
      }

      return false; // Redirect unauthenticated users to login page
    },
  },
});
