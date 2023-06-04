# from abc import ABC
#
# from django.contrib.auth.hashers import make_password
# from django.contrib.auth.models import User
from rest_framework import serializers

from kinokino.models import UserProfile, Movie


class MovieSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    kinopoisk_id = serializers.IntegerField()
    name = serializers.CharField(max_length=50)
    year = serializers.IntegerField()
    type = serializers.ChoiceField(choices=Movie.TYPE_MOVIE)
    seasons_count = serializers.IntegerField(required=False)
    release_year_start = serializers.IntegerField(required=False)
    release_year_end = serializers.IntegerField(required=False)
    episodes_count = serializers.IntegerField(required=False)
    preview_url = serializers.CharField(max_length=150)
    favorite = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    def create(self, validated_data):
        """
        Create and return a new `Movie` instance, given the validated data.
        """
        return Movie.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Movie` instance, given the validated data.
        """
        instance.kinopoisk_id = validated_data.get('kinopoisk_id', instance.kinopoisk_id)
        instance.name = validated_data.get('name', instance.name)
        instance.year = validated_data.get('year', instance.year)
        instance.type = validated_data.get('type', instance.type)
        instance.seasons_count = validated_data.get('seasons_count', instance.seasons_count)
        instance.release_year_start = validated_data.get('release_year_start', instance.release_year_start)
        instance.release_year_end = validated_data.get('release_year_end', instance.release_year_end)
        instance.episodes_count = validated_data.get('episodes_count', instance.episodes_count)
        instance.preview_url = validated_data.get('preview_url', instance.preview_url)
        instance.favorite = validated_data.get('favorite', instance.favorite)
        instance.save()
        return instance


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)


class SearchingApiSerializer(serializers.Serializer):
    name = serializers.CharField()


class AddMovieSerializer(serializers.Serializer):
    number = serializers.CharField()
    name = serializers.CharField()
    username = serializers.CharField()


class UserMoviesSerializer(serializers.Serializer):
    username = serializers.CharField()
    field_name = serializers.CharField()


class MovieInfoSerializer(serializers.Serializer):
    username = serializers.CharField()
    movie_id = serializers.CharField()


class FavoriteMovieSerializer(serializers.Serializer):
    username = serializers.CharField()
    movie_id = serializers.CharField()
    fav = serializers.CharField()


class MovieStatusSerializer(serializers.Serializer):
    username = serializers.CharField()
    movie_id = serializers.CharField()
    status = serializers.CharField()


class SeasonsEpisodesSerializer(serializers.Serializer):
    username = serializers.CharField()
    movie_id = serializers.CharField()
    season_number = serializers.CharField()


class CompleteEpisodeSerializer(serializers.Serializer):
    username = serializers.CharField()
    movie_id = serializers.CharField()
    season_number = serializers.CharField()
    episode_number = serializers.CharField()
    complete = serializers.CharField()
