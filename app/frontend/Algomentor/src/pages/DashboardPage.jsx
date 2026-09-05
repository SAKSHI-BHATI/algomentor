import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Flame, TrendingUp, Target, Clock, ArrowRight, Sparkles } from 'lucide-react';
import Card from '../components/Card';
import Badge from '../components/Badge';
import ProgressBar from '../components/ProgressBar';
import Button from '../components/Button';
import { userProfile as mockProfile, skillProgress as mockSkills, recentActivity } from '../data/mockData';
import { getGreeting } from '../utils/helpers';
import { cn } from '../lib/utils';
import AvatarBuilder from '../layout/AvatarBuilder';
import TodoCompactCard from "../components/TodoCompactCard";
import { fetchDashboardData } from '../api';

const DashboardPage = () => {
  const navigate = useNavigate();
  const [openAvatar, setOpenAvatar] = useState(false);
  const [profile, setProfile] = useState(mockProfile);
  const [recommendations, setRecommendations] = useState([]);
  const [skills, setSkills] = useState(mockSkills);

  useEffect(() => {
    const loadDashboard = async () => {
      const res = await fetchDashboardData();
      if (res.success) {
        if (res.profile) setProfile(res.profile);
        if (res.recommendations) setRecommendations(res.recommendations);
        if (res.skill_progress) setSkills(res.skill_progress);
      }
    };
    loadDashboard();
  }, []);

  return (
    <div className="px-8 pt-8 pb-10 max-w-7xl mx-auto space-y-8">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">
            {getGreeting()}, {profile.name}
          </h1>
          <p className="text-lg text-slate-600">
            Ready to sharpen your algorithmic thinking today?
          </p>
        </div>

        <button
          onClick={() => setOpenAvatar(true)}
          className="w-14 h-14 rounded-full bg-indigo-600 text-white flex items-center justify-center shadow-md hover:scale-105 transition text-2xl"
          title="Customize Avatar"
        >
          🤖
        </button>
      </div>

      {/* Overview Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Streak */}
        <Card className="p-6 h-[190px] flex flex-col justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-orange-50 rounded-2xl flex items-center justify-center">
              <Flame className="w-6 h-6 text-orange-500" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Current Streak</p>
              <p className="text-2xl font-bold text-slate-900">{profile.streak || 7} days</p>
            </div>
          </div>
          <p className="text-xs text-slate-500">Daily practice active 🚀</p>
        </Card>

        {/* Problems */}
        <Card className="p-6 h-[190px] flex flex-col justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-indigo-50 rounded-2xl flex items-center justify-center">
              <Target className="w-6 h-6 text-indigo-600" />
            </div>
            <div>
              <p className="text-sm text-slate-500">Problems Solved</p>
              <p className="text-2xl font-bold text-slate-900">{profile.solved_count || 5} / {profile.total_problems || 10}</p>
            </div>
          </div>
          <p className="text-xs text-slate-500">Across canonical topics</p>
        </Card>

        {/* Level */}
        <Card className="p-4 h-[190px] flex flex-col justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-violet-50 rounded-2xl flex items-center justify-center">
              <TrendingUp className="w-6 h-6 text-violet-600" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <p className="text-sm text-slate-500">Mastery Level</p>
                <Badge variant="primary" className="text-xs px-2 py-1">{profile.level || 'Intermediate'}</Badge>
              </div>
              <p className="text-xl font-bold text-slate-900 mt-1">Level 3</p>
            </div>
          </div>
          <ProgressBar value={65} label="Progress to Advanced" />
        </Card>

        {/* Compact Todo */}
        <TodoCompactCard width="w-full" height="h-[190px]" large />
      </div>

      {/* Personalized Recommendations Section */}
      {recommendations.length > 0 && (
        <Card className="p-6 bg-gradient-to-r from-indigo-900 via-indigo-800 to-purple-900 text-white border-none shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-400" />
              <h2 className="text-xl font-bold">Personalized AI Problem Recommendations</h2>
            </div>
            <span className="text-xs text-indigo-200">Based on your weak topics</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                onClick={() => navigate(`/problems/workspace/${rec.id}`)}
                className="p-4 bg-white/10 backdrop-blur-md rounded-xl border border-white/20 hover:bg-white/20 transition cursor-pointer flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-white text-base">{rec.title}</span>
                    <Badge variant="secondary" className="text-xs">{rec.difficulty}</Badge>
                  </div>
                  <p className="text-xs text-indigo-200">{rec.reasoning}</p>
                </div>
                <Button size="sm" className="bg-white text-indigo-900 hover:bg-indigo-50">
                  Solve <ArrowRight className="w-4 h-4 ml-1 inline" />
                </Button>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Lower Grid: Skills & Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-6">Topic Skill Progress</h2>
          <div className="space-y-5">
            {skills.map((skill) => (
              <div key={skill.name}>
                <div className="flex justify-between mb-2">
                  <span className="text-sm font-medium text-slate-700">{skill.name}</span>
                  <span className="text-sm text-slate-600 font-semibold">{skill.progress}%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${skill.progress}%` }}
                    transition={{ duration: 1 }}
                    className="h-full bg-gradient-to-r from-indigo-600 to-violet-600"
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-slate-900">Recent Learning Activity</h2>
            <Clock className="w-5 h-5 text-slate-400" />
          </div>

          <div className="space-y-4">
            {recentActivity.map((activity, index) => (
              <div key={index} className="flex items-center justify-between p-3 rounded-lg hover:bg-slate-50 border border-slate-100">
                <div>
                  <p className="font-medium text-slate-900">{activity.problem}</p>
                  <p className="text-xs text-slate-500">{activity.date}</p>
                </div>

                <div className="flex items-center gap-3">
                  <Badge>{activity.difficulty}</Badge>
                  <div className={cn(
                    "w-2.5 h-2.5 rounded-full",
                    activity.status === 'Completed' ? 'bg-emerald-500' : 'bg-amber-500'
                  )}/>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Avatar Modal */}
      {openAvatar && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl shadow-xl w-[760px] max-w-[92vw] h-[82vh] flex overflow-hidden relative">
            <button
              onClick={() => setOpenAvatar(false)}
              className="absolute top-4 right-4 text-slate-500 hover:text-black z-10 font-bold"
            >
              ✕
            </button>
            <div className="w-1/2 bg-slate-100 flex items-center justify-center">
              <div className="h-[85%] w-full flex items-center justify-center">
                <AvatarBuilder previewOnly />
              </div>
            </div>
            <div className="w-1/2 p-6 overflow-y-auto">
              <AvatarBuilder controlsOnly />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
