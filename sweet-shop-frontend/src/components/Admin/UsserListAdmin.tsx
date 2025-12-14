// src/components/Admin/UserListAdmin.tsx

import React, { useState, useEffect } from 'react';
import api from '../../api/index.ts'; 
import useAuth from '../../hooks/useAuth.ts';

// --- Type Definitions ---
interface User {
    id: number;
    email: string;
    is_admin: boolean;
    // Assuming backend returns created_at for extra info
    created_at: string; 
}

const UserListAdmin: React.FC = () => {
    const { user: currentUser } = useAuth(); // Rename user to currentUser to avoid confusion
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Fetch the list of all registered users
    const fetchUsers = async () => {
        setLoading(true);
        try {
            // Assuming Admin has access to a dedicated /users/ endpoint
            const response = await api.get<User[]>('/users/'); 
            setUsers(response.data);
            setError(null);
        } catch (err) {
            console.error('Failed to fetch users:', err);
            setError('Failed to load user list. Check the backend endpoint /users/.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (currentUser?.is_admin) {
            fetchUsers();
        }
    }, [currentUser]);

    // Handle toggling a user's admin status
    const handleToggleAdmin = async (targetUserId: number, currentStatus: boolean) => {
        // Prevent an admin from demoting themselves!
        if (targetUserId === currentUser?.id) {
            alert("You cannot change your own admin status.");
            return;
        }

        const newStatus = !currentStatus;
        const action = newStatus ? 'promote' : 'demote';

        if (!window.confirm(`Are you sure you want to ${action} this user?`)) {
            return;
        }

        try {
            // Assuming a PATCH endpoint like /users/{id}/admin
            await api.patch(`/users/${targetUserId}/admin`, { is_admin: newStatus });
            
            // Update the local state
            setUsers(prevUsers => prevUsers.map(user => 
                user.id === targetUserId ? { ...user, is_admin: newStatus } : user
            ));
            alert(`User status updated successfully (${action}d).`);

        } catch (err) {
            console.error('Admin status toggle failed:', err);
            alert('Failed to update user admin status.');
        }
    };
    
    // Safety check (AdminRoute handles this, but good practice)
    if (!currentUser || !currentUser.is_admin) {
        return <div className="alert alert-danger mt-5 text-center">Unauthorized Access.</div>;
    }

    if (loading) {
        return <div className="text-center mt-5">Loading user accounts...</div>;
    }

    if (error) {
        return <div className="alert alert-danger mt-5 text-center">{error}</div>;
    }

    return (
        <div className="container mt-4">
            <h2 className="mb-4">User Account Management</h2>
            
            {users.length === 0 ? (
                <div className="alert alert-info text-center">
                    No users registered yet.
                </div>
            ) : (
                <table className="table table-striped table-hover shadow-sm">
                    <thead className="table-dark">
                        <tr>
                            <th>ID</th>
                            <th>Email</th>
                            <th>Status</th>
                            <th>Registered On</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((user) => (
                            <tr key={user.id}>
                                <td>{user.id}</td>
                                <td>{user.email}</td>
                                <td>
                                    <span className={`badge ${user.is_admin ? 'bg-success' : 'bg-primary'}`}>
                                        {user.is_admin ? 'Admin' : 'Standard User'}
                                    </span>
                                </td>
                                <td>{new Date(user.created_at).toLocaleDateString()}</td>
                                <td>
                                    <button 
                                        className={`btn btn-sm ${user.is_admin ? 'btn-danger' : 'btn-success'}`}
                                        onClick={() => handleToggleAdmin(user.id, user.is_admin)}
                                        // Disable button for the current logged-in user
                                        disabled={user.id === currentUser.id} 
                                    >
                                        {user.is_admin ? 'Demote' : 'Promote to Admin'}
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default UserListAdmin;