import axios from 'axios';

const client = axios.create({
    baseURL: '/api', // Proxy will handle this in Vite
    headers: {
        'Content-Type': 'application/json',
    },
});

export default client;
